#include <glad.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>
#include <cstdio>
#include <cstdlib>
#include <thread>
#include <chrono>

const unsigned int WIDTH = 800;
const unsigned int HEIGHT = 800;

// Current window dimensions (may change after resize)
int currentWidth = WIDTH;
int currentHeight = HEIGHT;

GLuint quadVAO, quadVBO;
GLuint simShader;
GLuint visShader;
GLuint transformShader; // Added shader for GPU-accelerated state transforms

// Define framebuffer and texture variables
GLuint tex1;
GLuint tex2;
GLuint fbo1;
GLuint fbo2;
GLuint transformFbo; // Added framebuffer for GPU-accelerated transforms
GLuint tempTexture;  // Temporary texture for transform operations

// FPS counter variables
float lastTime = 0.0f;
float frameTime = 0.0f;
int frameCount = 0;
float fps = 0.0f;
float fpsUpdateInterval = 0.5f; // Update FPS display every half second
float deltaTime = 0.0f; // Time between current frame and last frame

// Frame rate limiting variables
bool limitFramerate = false;
int maxFramerate = 60;
float targetFrameTime = 1.0f / 60.0f;

// UI visibility toggle
bool showUI = true;
bool tabPressed = false;

// Pan and zoom variables
float zoomFactor = 1.0f;
float panX = 0.0f;
float panY = 0.0f;
// Previous pan and zoom state for tracking changes
float prevZoomFactor = 1.0f;
float prevPanX = 0.0f;
float prevPanY = 0.0f;
bool needsStateTransform = false;
bool isDragging = false;
double lastMouseX = 0.0f;
double lastMouseY = 0.0f;
float mouseWheelSensitivity = 0.1f; // Zoom sensitivity

const float quadVertices[] = {
    // positions   // texCoords
    -1.0f,  1.0f,  0.0f, 1.0f,
    -1.0f, -1.0f,  0.0f, 0.0f,
     1.0f, -1.0f,  1.0f, 0.0f,

    -1.0f,  1.0f,  0.0f, 1.0f,
     1.0f, -1.0f,  1.0f, 0.0f,
     1.0f,  1.0f,  1.0f, 1.0f
};

GLuint loadShader(GLenum type, const std::string& path) {
    std::ifstream f(path);
    std::stringstream ss;
    ss << f.rdbuf();
    std::string src = ss.str();
    const char* c_str = src.c_str();
    GLuint shader = glCreateShader(type);
    glShaderSource(shader, 1, &c_str, nullptr);
    glCompileShader(shader);

    GLint success;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        char log[512]; glGetShaderInfoLog(shader, 512, nullptr, log);
        std::cerr << "Shader compile error:\n" << log << std::endl;
    }
    return shader;
}

GLuint createProgram(const std::string& vsPath, const std::string& fsPath) {
    GLuint vs = loadShader(GL_VERTEX_SHADER, vsPath);
    GLuint fs = loadShader(GL_FRAGMENT_SHADER, fsPath);
    GLuint prog = glCreateProgram();
    glAttachShader(prog, vs);
    glAttachShader(prog, fs);
    glLinkProgram(prog);

    GLint success;
    glGetProgramiv(prog, GL_LINK_STATUS, &success);
    if (!success) {
        char log[512]; glGetProgramInfoLog(prog, 512, nullptr, log);
        std::cerr << fsPath << std::endl;
        std::cerr << "Program link error:\n" << log << std::endl;
    }

    glDeleteShader(vs);
    glDeleteShader(fs);
    return prog;
}

void setupQuad() {
    glGenVertexArrays(1, &quadVAO);
    glGenBuffers(1, &quadVBO);
    glBindVertexArray(quadVAO);
    glBindBuffer(GL_ARRAY_BUFFER, quadVBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(quadVertices), quadVertices, GL_STATIC_DRAW);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)(2 * sizeof(float)));
    glEnableVertexAttribArray(1);
}

void renderQuad() {
    glBindVertexArray(quadVAO);
    glDrawArrays(GL_TRIANGLES, 0, 6);
}

GLuint createFramebuffer(GLuint& texOut, int width, int height) {
    GLuint fbo, tex;
    glGenFramebuffers(1, &fbo);
    glGenTextures(1, &tex);
    glBindTexture(GL_TEXTURE_2D, tex);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, width, height, 0, GL_RGBA, GL_FLOAT, nullptr);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    glBindFramebuffer(GL_FRAMEBUFFER, fbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0);

    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
        std::cerr << "Framebuffer not complete!" << std::endl;

    texOut = tex;
    return fbo;
}

void initState(GLuint tex, int width, int height) {
    std::vector<float> data(width * height * 4, 0.0f);
    for (int y = height / 2 - 10; y < height / 2 + 10; ++y)
        for (int x = width / 2 - 10; x < width / 2 + 10; ++x) {
            int i = (y * width + x) * 4;
            data[i]     = 1.0f;  // U = 1.0 (full concentration)
            data[i + 1] = 1.0f;  // V = 1.0 (seed)
    }

    glBindTexture(GL_TEXTURE_2D, tex);
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, width, height, GL_RGBA, GL_FLOAT, data.data());
}

void preserveStateOnResize(GLuint oldTex, GLuint newTex, int oldWidth, int oldHeight, int newWidth, int newHeight) {
    // Allocate buffer for the old state data
    std::vector<float> oldData(oldWidth * oldHeight * 4);
    
    // Read the current state
    glBindTexture(GL_TEXTURE_2D, oldTex);
    glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_FLOAT, oldData.data());
    
    // Allocate buffer for the new state (initialized to 0.0f)
    std::vector<float> newData(newWidth * newHeight * 4, 0.0f);
    
    // Copy the old state into the new state, preserving as much as possible
    int copyWidth = std::min(oldWidth, newWidth);
    int copyHeight = std::min(oldHeight, newHeight);
    
    for (int y = 0; y < copyHeight; y++) {
        for (int x = 0; x < copyWidth; x++) {
            int oldIdx = (y * oldWidth + x) * 4;
            int newIdx = (y * newWidth + x) * 4;
            
            newData[newIdx]     = oldData[oldIdx];     // U component
            newData[newIdx + 1] = oldData[oldIdx + 1]; // V component
            // Components 2 and 3 remain 0.0f
        }
    }
    
    // Upload the new data
    glBindTexture(GL_TEXTURE_2D, newTex);
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, newWidth, newHeight, GL_RGBA, GL_FLOAT, newData.data());
}

// Transform simulation state after pan/zoom changes
void translateState(GLuint tex, int width, int height, float oldZoom, float oldPanX, float oldPanY, float newZoom, float newPanX, float newPanY) {
    // Make sure we have a valid texture
    if (tex == 0) {
        std::cerr << "Error in translateState: Invalid texture ID" << std::endl;
        return;
    }
    
    // Check for valid dimensions
    if (width <= 0 || height <= 0) {
        std::cerr << "Error in translateState: Invalid dimensions" << std::endl;
        return;
    }
    
    try {
        // Allocate buffer for the current state data with proper error handling
        std::vector<float> currentData(width * height * 4, 0.0f);
        
        // Make sure we're dealing with the right texture
        glBindTexture(GL_TEXTURE_2D, tex);
        
        // Check for OpenGL errors before the critical call
        GLenum err = glGetError();
        if (err != GL_NO_ERROR) {
            std::cerr << "OpenGL error before glGetTexImage: " << err << std::endl;
            return;
        }
        
        // Read the current state
        glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_FLOAT, currentData.data());
        
        // Check for OpenGL errors after the critical call
        err = glGetError();
        if (err != GL_NO_ERROR) {
            std::cerr << "OpenGL error after glGetTexImage: " << err << std::endl;
            return;
        }
        
        // Allocate buffer for the transformed state
        std::vector<float> transformedData(width * height * 4, 0.0f);
        
        // Apply the transformation for each pixel in the new view
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                // Convert pixel coordinates to NDC space [0,1]
                float ndcX = (float)x / width;
                float ndcY = (float)y / height;
                
                // Convert NDC to world space using the new transformation
                float worldX = (ndcX - 0.5f) / newZoom + 0.5f - newPanX / newZoom;
                float worldY = (ndcY - 0.5f) / newZoom + 0.5f - newPanY / newZoom;
                
                // Convert world space back to NDC using the old transformation
                float oldNdcX = (worldX + oldPanX / oldZoom - 0.5f) * oldZoom + 0.5f;
                float oldNdcY = (worldY + oldPanY / oldZoom - 0.5f) * oldZoom + 0.5f;
                
                // Convert NDC back to pixel coordinates in the old view
                int srcX = (int)(oldNdcX * width);
                int srcY = (int)(oldNdcY * height);
                
                // Destination index in transformed data
                int dstIdx = (y * width + x) * 4;
                
                // Check if source coordinates are within bounds
                if (srcX >= 0 && srcX < width && srcY >= 0 && srcY < height) {
                    // Source index in current data
                    int srcIdx = (srcY * width + srcX) * 4;
                    
                    // Make sure we're not accessing out of bounds memory
                    if (srcIdx >= 0 && srcIdx < (width * height * 4) && 
                        dstIdx >= 0 && dstIdx < (width * height * 4)) {
                        // Copy the U and V values
                        transformedData[dstIdx]     = currentData[srcIdx];     // U component
                        transformedData[dstIdx + 1] = currentData[srcIdx + 1]; // V component
                        // Components 2 and 3 remain 0.0f
                    }
                }
                // Out of bounds pixels remain at 0
            }
        }
        
        // Check for errors before uploading texture
        err = glGetError();
        if (err != GL_NO_ERROR) {
            std::cerr << "OpenGL error before texture upload: " << err << std::endl;
            return;
        }
        
        // Upload the transformed data back to the texture
        glBindTexture(GL_TEXTURE_2D, tex);
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, width, height, GL_RGBA, GL_FLOAT, transformedData.data());
        
        // Final error check
        err = glGetError();
        if (err != GL_NO_ERROR) {
            std::cerr << "OpenGL error after texture upload: " << err << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "Exception in translateState: " << e.what() << std::endl;
    } catch (...) {
        std::cerr << "Unknown exception in translateState" << std::endl;
    }
}

// GPU-accelerated transform of simulation state after pan/zoom changes
void translateStateGPU(GLuint srcTex, GLuint destTex, int width, int height, float oldZoom, float oldPanX, float oldPanY, float newZoom, float newPanX, float newPanY) {
    // Make sure we have valid textures
    if (srcTex == 0 || destTex == 0) {
        std::cerr << "Error in translateStateGPU: Invalid texture ID" << std::endl;
        return;
    }
    
    // Check for valid dimensions
    if (width <= 0 || height <= 0) {
        std::cerr << "Error in translateStateGPU: Invalid dimensions" << std::endl;
        return;
    }
    
    // Use the transform shader
    glUseProgram(transformShader);
    
    // Set transformation uniforms
    glUniform1f(glGetUniformLocation(transformShader, "oldZoom"), oldZoom);
    glUniform1f(glGetUniformLocation(transformShader, "newZoom"), newZoom);
    glUniform2f(glGetUniformLocation(transformShader, "oldPan"), oldPanX, oldPanY);
    glUniform2f(glGetUniformLocation(transformShader, "newPan"), newPanX, newPanY);
    
    // Bind source texture
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, srcTex);
    glUniform1i(glGetUniformLocation(transformShader, "inputTexture"), 0);
    
    // Render to destination texture
    glBindFramebuffer(GL_FRAMEBUFFER, transformFbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, destTex, 0);
    
    // Check framebuffer status
    GLenum status = glCheckFramebufferStatus(GL_FRAMEBUFFER);
    if (status != GL_FRAMEBUFFER_COMPLETE) {
        std::cerr << "Error: Framebuffer is not complete! Status: " << status << std::endl;
        return;
    }
    
    // Set viewport to match the texture dimensions
    glViewport(0, 0, width, height);
    
    // Render a quad to apply the transformation
    renderQuad();
    
    // Reset default framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    
    // Check for errors
    GLenum err = glGetError();
    if (err != GL_NO_ERROR) {
        std::cerr << "OpenGL error in translateStateGPU: " << err << std::endl;
    }
}

FILE* ffmpegPipe = nullptr;

void startFFmpegRecording() {
    const char* ffmpegCommand = "ffmpeg -y -f rawvideo -vcodec rawvideo -pix_fmt rgba -s 800x800 -r 60 -i - -vf vflip -vcodec libx264 -crf 18 -preset fast output.mp4";
    ffmpegPipe = _popen(ffmpegCommand, "wb");
    if (!ffmpegPipe) {
        std::cerr << "Failed to open FFmpeg pipe." << std::endl;
        exit(1);
    }
}

void stopFFmpegRecording() {
    if (ffmpegPipe) {
        _pclose(ffmpegPipe);
        ffmpegPipe = nullptr;
    }
}

void captureFrame() {
    if (!ffmpegPipe) return;

    std::vector<unsigned char> pixels(WIDTH * HEIGHT * 4);
    glReadPixels(0, 0, WIDTH, HEIGHT, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    fwrite(pixels.data(), sizeof(unsigned char), pixels.size(), ffmpegPipe);
}

void resizeScreen(GLFWwindow* window, int width, int height, GLuint simShader, GLuint visShader, GLuint& tex1, GLuint& tex2, GLuint& fbo1, GLuint& fbo2) {
    static int oldWidth = WIDTH;
    static int oldHeight = HEIGHT;
    
    // Update global current dimensions
    currentWidth = width;
    currentHeight = height;
    
    glViewport(0, 0, width, height);

    //std::cout << "Resizing to: " << width << "x" << height << std::endl;

    // Update resolution and dx/dy uniforms dynamically
    glUseProgram(simShader);
    glUniform2f(glGetUniformLocation(simShader, "resolution"), (float)width, (float)height);
    glUniform2f(glGetUniformLocation(simShader, "dx"), 1.0f / width, 1.0f / height);

    glUseProgram(visShader);
    glUniform2f(glGetUniformLocation(visShader, "resolution"), (float)width, (float)height);

    // Create new framebuffers with the new dimensions
    GLuint newTex1, newTex2;
    GLuint newFbo1 = createFramebuffer(newTex1, width, height);
    GLuint newFbo2 = createFramebuffer(newTex2, width, height);

    // Preserve the state from the old textures to the new textures
    preserveStateOnResize(tex1, newTex1, oldWidth, oldHeight, width, height);
    preserveStateOnResize(tex2, newTex2, oldWidth, oldHeight, width, height);
    
    // Delete old textures and framebuffers after preserving state
    glDeleteTextures(1, &tex1);
    glDeleteTextures(1, &tex2);
    glDeleteFramebuffers(1, &fbo1);
    glDeleteFramebuffers(1, &fbo2);
    
    // Update references to the new textures and framebuffers
    tex1 = newTex1;
    tex2 = newTex2;
    fbo1 = newFbo1;
    fbo2 = newFbo2;
    
    // Remember current size for next resize
    oldWidth = width;
    oldHeight = height;
}

// Update framebuffer_size_callback to pass shader program IDs
void framebuffer_size_callback(GLFWwindow* window, int width, int height) {
    extern GLuint simShader, visShader; // Declare external shader program IDs
    extern GLuint tex1, tex2, fbo1, fbo2; // Declare external textures and framebuffers
    resizeScreen(window, width, height, simShader, visShader, tex1, tex2, fbo1, fbo2);
}

// Mouse callback for handling pan/zoom interactions
void mouse_button_callback(GLFWwindow* window, int button, int action, int mods) {
    ImGuiIO& io = ImGui::GetIO();
    if (io.WantCaptureMouse) {
        return; // Skip if ImGui is using the mouse
    }
    
    if (button == GLFW_MOUSE_BUTTON_LEFT) {
        if (action == GLFW_PRESS) {
            isDragging = true;
            glfwGetCursorPos(window, &lastMouseX, &lastMouseY);
        } else if (action == GLFW_RELEASE) {
            isDragging = false;
        }
    }
}

// Cursor position callback for panning
void cursor_position_callback(GLFWwindow* window, double xpos, double ypos) {
    extern float deltaTime;
    extern int currentWidth, currentHeight;
    ImGuiIO& io = ImGui::GetIO();
    if (io.WantCaptureMouse) {
        return; // Skip if ImGui is using the mouse
    }
    
    if (isDragging) {
        // Store previous pan values
        prevPanX = panX;
        prevPanY = panY;
        
        double dx = xpos - lastMouseX;
        double dy = ypos - lastMouseY;
        
        // Define a constant base speed for panning (units per second)
        const float BASE_PAN_SPEED = 2.0f;
        
        // Scale the pan amount by zoom factor and deltaTime for consistent speed
        float panSpeed = BASE_PAN_SPEED / zoomFactor;
        panX += (float)(dx / currentWidth) * panSpeed;
        panY -= (float)(dy / currentHeight) * panSpeed; // Invert Y for correct panning direction
        
        lastMouseX = xpos;
        lastMouseY = ypos;
        
        // Check if pan change is significant enough to require state transformation
        float panChangeThreshold = 0.01f; // Adjust this threshold as needed
        if (abs(panX - prevPanX) > panChangeThreshold || abs(panY - prevPanY) > panChangeThreshold) {
            needsStateTransform = true;
        }
    }
}

// Scroll callback for zooming
void scroll_callback(GLFWwindow* window, double xoffset, double yoffset) {
    extern float deltaTime;
    extern int currentWidth, currentHeight;
    ImGuiIO& io = ImGui::GetIO();
    if (io.WantCaptureMouse) {
        return; // Skip if ImGui is using the mouse
    }
    
    // Store previous zoom and pan values
    prevZoomFactor = zoomFactor;
    prevPanX = panX;
    prevPanY = panY;
    
    // Define a base zoom speed (units per second)
    const float BASE_ZOOM_SPEED = 1.0f;
    
    // Adjust zoom factor based on scroll direction with consistent speed
    float zoomDelta = (float)yoffset * mouseWheelSensitivity * BASE_ZOOM_SPEED;
    
    // Get cursor position for zoom targeting
    double mouseX, mouseY;
    glfwGetCursorPos(window, &mouseX, &mouseY);
    
    // Convert mouse position to normalized device coordinates
    float ndcX = (float)(mouseX / currentWidth) * 2.0f - 1.0f;
    float ndcY = -((float)(mouseY / currentHeight) * 2.0f - 1.0f);  // Flip Y coordinate
    
    // Calculate zoom target in world space
    float worldX = (ndcX - panX) / zoomFactor;
    float worldY = (ndcY - panY) / zoomFactor;
    
    // Update zoom factor
    float prevZoom = zoomFactor;
    zoomFactor *= (1.0f + zoomDelta);
    zoomFactor = std::max(0.1f, std::min(zoomFactor, 10.0f));  // Limit zoom range
    
    // Adjust pan to keep mouse position fixed on the same world position
    if (zoomFactor != prevZoom) {
        panX = ndcX - worldX * zoomFactor;
        panY = ndcY - worldY * zoomFactor;
        
        // Check if zoom change is significant enough to require state transformation
        float zoomChangeThreshold = 0.1f; // Adjust this threshold as needed
        if (abs(zoomFactor - prevZoomFactor) > zoomChangeThreshold) {
            needsStateTransform = true;
        }
    }
}

void processInput(GLFWwindow* window) {
    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
        glfwSetWindowShouldClose(window, true);
    }

    if (glfwGetKey(window, GLFW_KEY_TAB) == GLFW_PRESS) {
        if (!tabPressed) {
            showUI = !showUI;
            tabPressed = true;
        }
    } else {
        tabPressed = false;
    }
    
    // Reset pan and zoom when 'R' key is pressed
    static bool rKeyPressed = false;
    if (glfwGetKey(window, GLFW_KEY_R) == GLFW_PRESS) {
        if (!rKeyPressed) {
            rKeyPressed = true;
            
            // Store current state for transformation
            prevZoomFactor = zoomFactor;
            prevPanX = panX;
            prevPanY = panY;
            
            // Mark for transformation
            if (zoomFactor != 1.0f || panX != 0.0f || panY != 0.0f) {
                needsStateTransform = true;
            }
            
            // Reset view immediately for visual feedback
            panX = 0.0f;
            panY = 0.0f;
            zoomFactor = 1.0f;
        }
    } else {
        rKeyPressed = false;
    }
}

int main() {
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    GLFWwindow* win = glfwCreateWindow(WIDTH, HEIGHT, "Reaction-Diffusion", nullptr, nullptr);
    glfwMakeContextCurrent(win);
    
    // Disable VSync (0 = no limit, 1 = VSync)
    glfwSwapInterval(0);

    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        std::cerr << "Failed to init GLAD\n";
        return -1;
    }

    // Register the framebuffer size callback
    glfwSetFramebufferSizeCallback(win, framebuffer_size_callback);

    // Register mouse callbacks
    glfwSetMouseButtonCallback(win, mouse_button_callback);
    glfwSetCursorPosCallback(win, cursor_position_callback);
    glfwSetScrollCallback(win, scroll_callback);

    // Initialize ImGui
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    ImGui::StyleColorsDark();
    ImGui_ImplGlfw_InitForOpenGL(win, true);
    ImGui_ImplOpenGL3_Init("#version 330");

    simShader = createProgram("shaders/pass_vert.glsl", "shaders/rd_frag.glsl");
    visShader = createProgram("shaders/pass_vert.glsl", "shaders/rd_visual.glsl");
    transformShader = createProgram("shaders/pass_vert.glsl", "shaders/transform_frag.glsl");

    setupQuad();

    // Initialize framebuffers with WIDTH and HEIGHT (will be resized on window resize)
    fbo1 = createFramebuffer(tex1, WIDTH, HEIGHT);
    fbo2 = createFramebuffer(tex2, WIDTH, HEIGHT);
    
    // Create transform framebuffer for GPU-accelerated pan/zoom operations
    glGenFramebuffers(1, &transformFbo);
    glGenTextures(1, &tempTexture);
    glBindTexture(GL_TEXTURE_2D, tempTexture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, WIDTH, HEIGHT, 0, GL_RGBA, GL_FLOAT, nullptr);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    initState(tex1, WIDTH, HEIGHT);

    glUseProgram(simShader);
    glUniform2f(glGetUniformLocation(simShader, "dx"), 1.0f / WIDTH, 1.0f / HEIGHT);

    // Set the resolution uniform for both shaders
    glUseProgram(simShader);
    glUniform2f(glGetUniformLocation(simShader, "resolution"), (float)WIDTH, (float)HEIGHT);

    glUseProgram(visShader);
    glUniform2f(glGetUniformLocation(visShader, "resolution"), (float)WIDTH, (float)HEIGHT);

    float feed = 0.037f;
    float kill = 0.06f;
    float diffU = 0.16f;
    float diffV = 0.08f;
    float dt = 0.1f;

    //startFFmpegRecording();

    while (!glfwWindowShouldClose(win)) {
        glfwPollEvents();
        processInput(win);

        // Start ImGui frame
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        if (showUI) {
            // Ensure the ImGui window is visible by setting its position and size
            ImGui::SetNextWindowPos(ImVec2(50, 50), ImGuiCond_FirstUseEver);
            ImGui::SetNextWindowSize(ImVec2(400, 300), ImGuiCond_FirstUseEver);

            ImGui::Begin("Reaction-Diffusion Parameters");
            ImGui::Text("FPS: %.1f", fps);  // Display FPS in the ImGui window
            
            // Framerate control
            ImGui::Checkbox("Limit Framerate", &limitFramerate);
            ImGui::SameLine();
            if (ImGui::Button("Unlimited")) {
                limitFramerate = false;
            }
            
            if (limitFramerate) {
                if (ImGui::SliderInt("Max FPS", &maxFramerate, 1, 1000)) {
                    targetFrameTime = 1.0f / maxFramerate;
                }
            }
            
            ImGui::SliderFloat("Feed (F)", &feed, 0.0f, 0.1f);
            ImGui::SliderFloat("Kill (k)", &kill, 0.0f, 0.1f);
            ImGui::SliderFloat("Diffusion U (du)", &diffU, 0.0f, 1.0f);
            ImGui::SliderFloat("Diffusion V (dv)", &diffV, 0.0f, 1.0f);
            ImGui::SliderFloat("Delta Time (dt)", &dt, 0.01f, 1.0f);
            
            // Pan and zoom controls
            if (ImGui::CollapsingHeader("Pan & Zoom Controls", ImGuiTreeNodeFlags_DefaultOpen)) {
                ImGui::SliderFloat("Zoom", &zoomFactor, 0.1f, 10.0f);
                ImGui::SliderFloat("Pan X", &panX, -2.0f, 2.0f);
                ImGui::SliderFloat("Pan Y", &panY, -2.0f, 2.0f);
                ImGui::SliderFloat("Zoom Speed", &mouseWheelSensitivity, 0.01f, 0.5f);
                
                if (ImGui::Button("Reset Pan/Zoom")) {
                    // Store current state for transformation
                    prevZoomFactor = zoomFactor;
                    prevPanX = panX;
                    prevPanY = panY;
                    
                    // Mark for transformation if needed
                    if (zoomFactor != 1.0f || panX != 0.0f || panY != 0.0f) {
                        needsStateTransform = true;
                    }
                    
                    // Reset view immediately for visual feedback
                    panX = 0.0f;
                    panY = 0.0f;
                    zoomFactor = 1.0f;
                }
            }
            
            ImGui::End();
        }

        ImGui::Render();

        // Simulate: tex1 -> tex2
        glUseProgram(simShader);
        glUniform1f(glGetUniformLocation(simShader, "feed"), feed);
        glUniform1f(glGetUniformLocation(simShader, "kill"), kill);
        glUniform1f(glGetUniformLocation(simShader, "diffU"), diffU);
        glUniform1f(glGetUniformLocation(simShader, "diffV"), diffV);
        glUniform1f(glGetUniformLocation(simShader, "dt"), dt);
        // Pass pan and zoom uniforms to simulation shader
        glUniform1f(glGetUniformLocation(simShader, "zoomFactor"), zoomFactor);
        glUniform2f(glGetUniformLocation(simShader, "panOffset"), panX, panY);
        
        glBindFramebuffer(GL_FRAMEBUFFER, fbo2);
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, tex1);
        glUniform1i(glGetUniformLocation(simShader, "currentState"), 0);
        renderQuad();

        // Visualize: tex2 -> screen
        glUseProgram(visShader);
        // Pass pan and zoom uniforms to visualization shader
        glUniform1f(glGetUniformLocation(visShader, "zoomFactor"), zoomFactor);
        glUniform2f(glGetUniformLocation(visShader, "panOffset"), panX, panY);
        
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        glBindTexture(GL_TEXTURE_2D, tex2);
        glUniform1i(glGetUniformLocation(visShader, "stateTexture"), 0);
        renderQuad();

        // Render ImGui
        if (showUI) {
            ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
        }

        // Swap textures
        std::swap(tex1, tex2);
        std::swap(fbo1, fbo2);

        // Update FPS counter
        float currentTime = glfwGetTime();
        deltaTime = currentTime - lastTime; // Calculate deltaTime
        frameTime += deltaTime;
        lastTime = currentTime;
        frameCount++;

        // Apply state transformation if needed
        if (needsStateTransform) {
            // Update tempTexture dimensions if needed
            static int lastWidth = currentWidth;
            static int lastHeight = currentHeight;
            if (lastWidth != currentWidth || lastHeight != currentHeight) {
                glBindTexture(GL_TEXTURE_2D, tempTexture);
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, currentWidth, currentHeight, 0, GL_RGBA, GL_FLOAT, nullptr);
                lastWidth = currentWidth;
                lastHeight = currentHeight;
            }
            
            // Apply transformation to tex1 using GPU
            translateStateGPU(tex1, tempTexture, currentWidth, currentHeight, prevZoomFactor, prevPanX, prevPanY, 1.0f, 0.0f, 0.0f);
            // Copy tempTexture back to tex1
            glBindFramebuffer(GL_FRAMEBUFFER, fbo1);
            glBindTexture(GL_TEXTURE_2D, tempTexture);
            glCopyTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, 0, 0, currentWidth, currentHeight);
            
            // Apply transformation to tex2 using GPU
            translateStateGPU(tex2, tempTexture, currentWidth, currentHeight, prevZoomFactor, prevPanX, prevPanY, 1.0f, 0.0f, 0.0f);
            // Copy tempTexture back to tex2
            glBindFramebuffer(GL_FRAMEBUFFER, fbo2);
            glBindTexture(GL_TEXTURE_2D, tempTexture);
            glCopyTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, 0, 0, currentWidth, currentHeight);
            
            // Reset framebuffer
            glBindFramebuffer(GL_FRAMEBUFFER, 0);
            
            // Update the previous state
            prevZoomFactor = zoomFactor;
            prevPanX = panX;
            prevPanY = panY;
            needsStateTransform = false;
            
            // After transformation, reset the view to normal since we've transformed the state itself
            panX = 0.0f;
            panY = 0.0f;
            zoomFactor = 1.0f;
            //std::cout << "Applied GPU-accelerated state transformation" << std::endl;
        }

        if (frameTime >= fpsUpdateInterval) {
            fps = frameCount / frameTime;
            frameTime = 0.0f;
            frameCount = 0;
        }

        // Apply frame rate limiting if enabled
        if (limitFramerate) {
            float frameEndTime = glfwGetTime();
            float elapsedTime = frameEndTime - currentTime;
            float sleepTime = targetFrameTime - elapsedTime;
            
            if (sleepTime > 0) {
                // Convert to milliseconds and sleep
                std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(sleepTime * 1000)));
            }
        }

        // Ensure ImGui is rendered after all other OpenGL rendering
        glfwSwapBuffers(win);
    }

    //stopFFmpegRecording();

    // Cleanup ImGui
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();

    glfwTerminate();
    return 0;
}