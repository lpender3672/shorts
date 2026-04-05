#ifdef _WIN32
#define NOMINMAX        // stop windows.h from defining min/max macros
#include <windows.h>    // defines WINGDIAPI and APIENTRY
#endif

#include <GL/glew.h>
#include <GLFW/glfw3.h>

#include <cuda.h>
#include <cuda_runtime.h>
#include <cuda_gl_interop.h>
#include <cstdio>
#include <cstdint>
#include <cmath>
#include <cassert>
#include <vector>

// -------------------- Tunables --------------------
#ifndef BALL_COUNT
#define BALL_COUNT (1u<<24)   // 16,777,216 by default
#endif
#ifndef RENDER_W
#define RENDER_W 1280
#endif
#ifndef RENDER_H
#define RENDER_H 720
#endif

static constexpr float WORLD_R     = 1.0f;   // container circle radius
static constexpr float BALL_R      = 0.0f;   // purely visual; no overlap checks
static constexpr float DT_SECONDS  = 0.002f; // sim step ~2 ms
static constexpr int   BLOCK_SIZE  = 256;    // tune per GPU
static constexpr float GRAVITY_Y = -0.8f;   // downward acceleration in world units/s^2
// --------------------------------------------------
// Mutable constants

__device__ __constant__ float gCamZoom;
__device__ __constant__ float gCamOffsetX;
__device__ __constant__ float gCamOffsetY;

__device__ __constant__ int gRenderW;
__device__ __constant__ int gRenderH;

// Error checks
#define CUDA_CHECK(x) do { cudaError_t err = (x); if (err != cudaSuccess) { \
  fprintf(stderr, "CUDA error %s at %s:%d\n", cudaGetErrorString(err), __FILE__, __LINE__); exit(1); } } while(0)

// RNG: stateless xorshift and float hash
__device__ __forceinline__ uint32_t xs32(uint32_t x){
  x ^= x<<13; x ^= x>>17; x ^= x<<5; return x;
}
__device__ __forceinline__ float u01(uint32_t x) {
  return (xs32(x) & 0x00FFFFFF) * (1.0f/16777216.0f);
}

// SoA state
struct State {
  float *x, *y;    // positions
  float *vx, *vy;  // velocities
};

// Device globals for interop
struct RenderBuf {
  uint32_t *density;   // RENDER_W * RENDER_H counters
  uchar4   *rgba;      // tonemapped pixels (PBO memory)
  uint32_t *max_bin;   // single-element max tracker
};

__device__ __forceinline__ void reflect_in_circle(float &px, float &py, float &vx, float &vy, float R)
{
    float r2 = px*px + py*py;
    float Rb = R - BALL_R;
    float R2 = Rb*Rb;

    // If far outside (resize artifact), delete
    if (r2 > R2 * 4.0f) {  // 2× radius outside → cull
        px = NAN; py = NAN;
        vx = 0.0f; vy = 0.0f;
        return;
    }

    // Regular boundary reflection
    if (r2 > R2) {
        float r  = sqrtf(r2);
        float nx = px / r;
        float ny = py / r;
        float vdotn = vx*nx + vy*ny;
        vx -= 2.0f*vdotn*nx;
        vy -= 2.0f*vdotn*ny;
        float back = Rb * (1.0f - 1e-4f);
        px = nx * back;
        py = ny * back;
    }
}

__global__ void kIntegrate(State s, uint32_t N, float dt){
  uint32_t i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i >= N) return;

  float px = s.x[i];
  float py = s.y[i];
  float vx = s.vx[i];
  float vy = s.vy[i];

  // apply gravity
  vy += GRAVITY_Y * dt;

  // integrate
  px = fmaf(vx, dt, px);
  py = fmaf(vy, dt, py);

  // boundary reflection
  reflect_in_circle(px, py, vx, vy, WORLD_R);

  s.x[i]  = px; s.y[i]  = py;
  s.vx[i] = vx; s.vy[i] = vy;
}

__global__ void kClearDensity(uint32_t* density, size_t n){
  uint32_t i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) density[i] = 0u;
}

__global__ void kClearMax(uint32_t* dmax){
  if (threadIdx.x==0 && blockIdx.x==0) *dmax = 0u;
}

__global__ void kBinToPixels(const State s, uint32_t N,
                             uint32_t* density, uint32_t* dmax)
{
  uint32_t i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i >= N) return;

  float px = (s.x[i] - gCamOffsetX) * gCamZoom;
  float py = (s.y[i] - gCamOffsetY) * gCamZoom;

  if (!isfinite(px) || !isfinite(py))
    return;

  int W = gRenderW;
  int H = gRenderH;

  float aspect = float(W) / float(H);
  float scaleX = (aspect >= 1.0f) ? (0.5f*H / WORLD_R) : (0.5f*W / WORLD_R);
  float scaleY = scaleX;

  int ix = int(px * scaleX + 0.5f*W);
  int iy = int(py * scaleY + 0.5f*H);

  if ((unsigned)ix < (unsigned)W && (unsigned)iy < (unsigned)H) {
    uint32_t idx = iy * W + ix;
    uint32_t val = atomicAdd(&density[idx], 1u) + 1u;
    atomicMax(dmax, val);
  }
}

__global__ void kToneMap(const uint32_t* density, uchar4* rgba, float exposure_k){
  uint32_t i = blockIdx.x * blockDim.x + threadIdx.x;
  uint32_t NP = gRenderW * gRenderH;
  if (i >= NP) return;

  float c = float(density[i]);          // count in this pixel
  float lum = 1.0f - expf(-exposure_k * c);  // filmic-ish exp curve
  uint8_t v = (uint8_t)fminf(255.0f, lum * 255.0f);
  rgba[i] = make_uchar4(v, v, v, 255);
}

// Host utility: initialize positions & velocities
__global__ void kInit(State s, uint32_t N)
{
    uint32_t i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;

    // Deterministic random seed
    uint32_t seed = 0x9E3779B9u ^ (i * 0x85EBCA6Bu);

    // Random angle around origin
    float a = u01(seed) * 2.0f * 3.14159265f;

    // Radius slightly inside the container
    float r = sqrtf(u01(seed ^ 0xA5A5A5A5u)) * (WORLD_R * 0.95f);

    // Small positional jitter to avoid perfect symmetry
    float jitter_r = (u01(seed ^ 0xC1C1C1C1u) - 0.5f) * 0.01f;   // ±0.005
    float jitter_a = (u01(seed ^ 0xB4B4B4B4u) - 0.5f) * 0.02f;   // ±~1°

    r += jitter_r;
    a += jitter_a;

    // Convert polar → Cartesian
    float px = r * cosf(a);
    float py = r * sinf(a);

    // Assign positions
    s.x[i] = px;
    s.y[i] = py;
    // Initial velocities zero
    s.vx[i] = 0;
    s.vy[i] = 0;
}

//
// ----------------------- OpenGL interop -----------------------
//
static GLuint gPBO = 0;
static GLuint gTex = 0;
static cudaGraphicsResource_t gCudaPBO = nullptr;

static void createGLObjects(int w, int h){
  // Texture
  glGenTextures(1, &gTex);
  glBindTexture(GL_TEXTURE_2D, gTex);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
  glBindTexture(GL_TEXTURE_2D, 0);

  // PBO
  glGenBuffers(1, &gPBO);
  glBindBuffer(GL_PIXEL_UNPACK_BUFFER, gPBO);
  glBufferData(GL_PIXEL_UNPACK_BUFFER, size_t(w)*size_t(h)*4, nullptr, GL_STREAM_DRAW);
  glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0);

  // Register PBO with CUDA
  CUDA_CHECK(cudaGraphicsGLRegisterBuffer(&gCudaPBO, gPBO, cudaGraphicsMapFlagsWriteDiscard));
}

static void drawFullscreenQuad(){
  glDisable(GL_DEPTH_TEST);
  glMatrixMode(GL_PROJECTION); glLoadIdentity();
  glOrtho(0, 1, 0, 1, -1, 1);
  glMatrixMode(GL_MODELVIEW); glLoadIdentity();

  glEnable(GL_TEXTURE_2D);
  glBindTexture(GL_TEXTURE_2D, gTex);

  glBegin(GL_QUADS);
    glTexCoord2f(0,0); glVertex2f(0,0);
    glTexCoord2f(1,0); glVertex2f(1,0);
    glTexCoord2f(1,1); glVertex2f(1,1);
    glTexCoord2f(0,1); glVertex2f(0,1);
  glEnd();

  glBindTexture(GL_TEXTURE_2D, 0);
  glDisable(GL_TEXTURE_2D);
}

struct AppContext {
    int width, height;
    int pendingW, pendingH;  // resize request
    RenderBuf rb;
    bool resizePending;
};

static bool dragging = false;
static double lastX = 0.0, lastY = 0.0;
static float hCamZoom    = 1.0f;
static float hCamOffsetX = 0.0f;
static float hCamOffsetY = 0.0f;

static void framebuffer_size_callback(GLFWwindow* window, int w, int h)
{
    AppContext* ctx = reinterpret_cast<AppContext*>(glfwGetWindowUserPointer(window));
    if (!ctx) return;
    ctx->pendingW = w;
    ctx->pendingH = h;
    ctx->resizePending = true;
}

static void scroll_callback(GLFWwindow*, double, double yoff) {
    hCamZoom *= powf(1.1f, (float)yoff);
    hCamZoom = fmaxf(0.1f, fminf(hCamZoom, 50.0f));
}

static void cursor_pos_callback(GLFWwindow* w, double x, double y) {
    if (!dragging) return;
    double dx = x - lastX;
    double dy = y - lastY;
    lastX = x;
    lastY = y;

    float world_dx = (float)(-dx / (0.5 * RENDER_H)) / hCamZoom;
    float world_dy = (float)( dy / (0.5 * RENDER_H)) / hCamZoom;
    hCamOffsetX += world_dx;
    hCamOffsetY += world_dy;
}

static void mouse_button_callback(GLFWwindow* w, int button, int action, int mods) {
    if (button == GLFW_MOUSE_BUTTON_RIGHT) {
        if (action == GLFW_PRESS) {
            dragging = true;
            glfwGetCursorPos(w, &lastX, &lastY);
        } else if (action == GLFW_RELEASE) {
            dragging = false;
        }
    }
}

int main(){
  AppContext ctx{};
  ctx.width = RENDER_W;
  ctx.height = RENDER_H;
  ctx.pendingW = RENDER_W;
  ctx.pendingH = RENDER_H;
  ctx.resizePending = false;
  
  // ---- GLFW window ----
  if (!glfwInit()) { fprintf(stderr,"GLFW init failed\n"); return 1; }
  //glfwWindowHint(GLFW_RESIZABLE, GLFW_FALSE);
  glfwWindowHint(GLFW_RESIZABLE, GLFW_TRUE);
  glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
  glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);
  GLFWwindow* win = glfwCreateWindow(RENDER_W, RENDER_H, "CUDA Circle Density (white=denser)", nullptr, nullptr);
  if (!win) { fprintf(stderr,"CreateWindow failed\n"); return 1; }
  glfwMakeContextCurrent(win);
  glfwSwapInterval(0); // vsync off

  glfwSetWindowUserPointer(win, &ctx);
  glfwSetFramebufferSizeCallback(win, framebuffer_size_callback);
  glfwSetScrollCallback(win, scroll_callback);
  glfwSetMouseButtonCallback(win, mouse_button_callback);
  glfwSetCursorPosCallback(win, cursor_pos_callback);

  // glewExperimental = GL_TRUE;
  if (glewInit() != GLEW_OK) {
    fprintf(stderr, "GLEW initialization failed\n");
    return 1;
  }

  createGLObjects(RENDER_W, RENDER_H);

  // ---- CUDA state ----
  State d;
  CUDA_CHECK(cudaMalloc(&d.x,  BALL_COUNT*sizeof(float)));
  CUDA_CHECK(cudaMalloc(&d.y,  BALL_COUNT*sizeof(float)));
  CUDA_CHECK(cudaMalloc(&d.vx, BALL_COUNT*sizeof(float)));
  CUDA_CHECK(cudaMalloc(&d.vy, BALL_COUNT*sizeof(float)));

  RenderBuf rb;
  CUDA_CHECK(cudaMalloc(&rb.density, RENDER_W*RENDER_H*sizeof(uint32_t)));
  CUDA_CHECK(cudaMalloc(&rb.max_bin, sizeof(uint32_t)));
  // rgba will point into mapped PBO each frame; no alloc here.

  CUDA_CHECK(cudaMemcpyToSymbol(gRenderW, &ctx.width, sizeof(int)));
  CUDA_CHECK(cudaMemcpyToSymbol(gRenderH, &ctx.height, sizeof(int)));

  // Init
  dim3 bs(BLOCK_SIZE);
  dim3 gs_sim( (BALL_COUNT + bs.x - 1)/bs.x );
  dim3 gs_den( ((RENDER_W*RENDER_H) + bs.x - 1)/bs.x );

  kInit<<<gs_sim, bs>>>(d, BALL_COUNT);
  CUDA_CHECK(cudaGetLastError());
  CUDA_CHECK(cudaDeviceSynchronize());


  // ---- CUDA Graph: one frame pipeline ----
  cudaStream_t stream;
  CUDA_CHECK(cudaStreamCreate(&stream));
  cudaGraph_t graph{};
  cudaGraphExec_t graphExec{};

  // We’ll build the graph once after mapping the PBO the first time.
  bool graph_built = false;

  while (!glfwWindowShouldClose(win)) {
    glfwPollEvents();

    

    CUDA_CHECK(cudaMemcpyToSymbol(gCamZoom,    &hCamZoom,    sizeof(float)));
    CUDA_CHECK(cudaMemcpyToSymbol(gCamOffsetX, &hCamOffsetX, sizeof(float)));
    CUDA_CHECK(cudaMemcpyToSymbol(gCamOffsetY, &hCamOffsetY, sizeof(float)));

    // Map PBO to CUDA
    CUDA_CHECK(cudaGraphicsMapResources(1, &gCudaPBO, 0));
    size_t pbo_size = 0;
    void* pbo_ptr = nullptr;
    CUDA_CHECK(cudaGraphicsResourceGetMappedPointer(&pbo_ptr, &pbo_size, gCudaPBO));
    rb.rgba = reinterpret_cast<uchar4*>(pbo_ptr);

    if (!graph_built) {
      // Capture graph for per-frame workload
      CUDA_CHECK(cudaStreamBeginCapture(stream, cudaStreamCaptureModeGlobal));

      // 1) Integrate motion
      kIntegrate<<<gs_sim, bs, 0, stream>>>(d, BALL_COUNT, DT_SECONDS);

      // 2) Clear density & max
      kClearDensity<<<gs_den, bs, 0, stream>>>(rb.density, RENDER_W*RENDER_H);
      kClearMax<<<1, 1, 0, stream>>>(rb.max_bin);

      // 3) Bin balls -> pixel density + track max
      kBinToPixels<<<gs_sim, bs, 0, stream>>>(d, BALL_COUNT, rb.density, rb.max_bin);

      // 4) Tone map into PBO (needs max)
      //    We need max value on host? No: just read device scalar.
      //    Use device-to-device copy to a local copy to read in kernel? Simpler:
      //    Launch a small kernel to fetch max to host isn’t necessary; we can copy the scalar.
      CUDA_CHECK(cudaStreamEndCapture(stream, &graph));
      CUDA_CHECK(cudaGraphInstantiate(&graphExec, graph, nullptr, nullptr, 0));
      graph_built = true;
    } else {
      // Re-launch captured part (steps 1..3)
      CUDA_CHECK(cudaGraphLaunch(graphExec, stream));
    }

    // Now we need maxBin value on host to pass as a parameter? We can avoid that by:
    // Launch kToneMap with max read via cudaMemcpyAsync into pinned host or simply copy to host scalar then kernel.
    // More efficient: copy to host scalar then launch tone-map with that arg (tiny overhead).
    // uint32_t hMax=0;
    // CUDA_CHECK(cudaMemcpyAsync(&hMax, rb.max_bin, sizeof(uint32_t), cudaMemcpyDeviceToHost, stream));
    // CUDA_CHECK(cudaStreamSynchronize(stream)); // ensure hMax ready

    // Tone-map
    // dim3 gs_pixels( ((RENDER_W*RENDER_H) + bs.x - 1)/bs.x );
    // kToneMap<<<gs_pixels, bs, 0, stream>>>(rb.density, rb.rgba, hMax);
    // CUDA_CHECK(cudaGetLastError());
    // CUDA_CHECK(cudaStreamSynchronize(stream));

    // --- Exposure smoothing (reduces flicker) ---
    static float exp_smooth = 0.0f;              // smoothed "reference max"
    static bool  exp_init   = false;

    uint32_t hMax = 0;
    CUDA_CHECK(cudaMemcpyAsync(&hMax, rb.max_bin, sizeof(uint32_t), cudaMemcpyDeviceToHost, stream));
    CUDA_CHECK(cudaStreamSynchronize(stream));

    // EWMA of max bin (tweak alpha for responsiveness)
    const float alpha = 0.10f;                   // 0.05..0.2 works well
    float target = float(hMax);

    // Optional clamping to keep exposure in a sane range (avoid huge swings)
    const float clampMin = 200.0f;
    const float clampMax = 4000.0f;
    target = fminf(clampMax, fmaxf(clampMin, target));

    if (!exp_init) { exp_smooth = target; exp_init = true; }
    else            { exp_smooth = (1.0f - alpha) * exp_smooth + alpha * target; }

    // Convert smoothed “max” to an exposure gain k.
    // We choose k so that ~25% of exp_smooth maps near white.
    // i.e., 1 - exp(-k * (0.25*exp_smooth)) ≈ 1  →  k ≈ ln(1+255)/(0.25*exp_smooth)
    float brightAt = 0.25f * fmaxf(exp_smooth, 1.0f);
    float exposure_k = logf(1.0f + 255.0f) / brightAt;

    // --- Tone-map with stable exposure ---
    dim3 gs_pixels( ((RENDER_W*RENDER_H) + bs.x - 1)/bs.x );
    kToneMap<<<gs_pixels, bs, 0, stream>>>(rb.density, rb.rgba, exposure_k);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaStreamSynchronize(stream));

    // Unmap PBO
    CUDA_CHECK(cudaGraphicsUnmapResources(1, &gCudaPBO, 0));

    // Blit PBO->Texture->Screen
    glBindBuffer(GL_PIXEL_UNPACK_BUFFER, gPBO);
    glBindTexture(GL_TEXTURE_2D, gTex);
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, RENDER_W, RENDER_H, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
    glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0);

    glClear(GL_COLOR_BUFFER_BIT);
    drawFullscreenQuad();
    glfwSwapBuffers(win);
  }

  // Cleanup
  if (graphExec) cudaGraphExecDestroy(graphExec);
  if (graph) cudaGraphDestroy(graph);
  cudaGraphicsUnregisterResource(gCudaPBO);
  glDeleteBuffers(1, &gPBO);
  glDeleteTextures(1, &gTex);
  cudaFree(d.x); cudaFree(d.y); cudaFree(d.vx); cudaFree(d.vy);
  cudaFree(rb.density); cudaFree(rb.max_bin);
  glfwDestroyWindow(win);
  glfwTerminate();
  return 0;
}
