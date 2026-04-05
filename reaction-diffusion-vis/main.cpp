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
#include <iomanip>

const unsigned int WIDTH = 800;
const unsigned int HEIGHT = 800;

// Current window dimensions (may change after resize)
int currentWidth = WIDTH;
int currentHeight = HEIGHT;

GLuint quadVAO, quadVBO;
GLuint simShader;
GLuint visShader;

// Define framebuffer and texture variables
GLuint tex1;
GLuint tex2;
GLuint fbo1;
GLuint fbo2;

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

// Pan and zoom variables (all in world UV space)
float zoomFactor = 1.0f;
float panX = 0.0f;
float panY = 0.0f;
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

    // U and W are fuel species — start at 1 everywhere
    for (int i = 0; i < width * height; ++i) {
        data[i * 4 + 0] = 1.0f; // U
        data[i * 4 + 2] = 1.0f; // W
    }

    // Seed V (system 1 activator) at centre
    for (int y = height / 2 - 10; y < height / 2 + 10; ++y)
        for (int x = width / 2 - 10; x < width / 2 + 10; ++x) {
            int i = (y * width + x) * 4;
            data[i + 0] = 0.5f;  // perturb U at seed
            data[i + 1] = 0.25f; // V seed
        }

    // Seed X (system 2 activator) at a different location (1/3, 2/3)
    int sx = width / 3, sy = height * 2 / 3;
    for (int y = sy - 10; y < sy + 10; ++y)
        for (int x = sx - 10; x < sx + 10; ++x) {
            int i = (y * width + x) * 4;
            data[i + 2] = 0.5f;  // perturb W at seed
            data[i + 3] = 0.25f; // X seed
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
    
    // Pre-fill new buffer: U=1, W=1 for any newly exposed area
    std::vector<float> newData(newWidth * newHeight * 4, 0.0f);
    for (int i = 0; i < newWidth * newHeight; ++i) {
        newData[i * 4 + 0] = 1.0f; // U fuel
        newData[i * 4 + 2] = 1.0f; // W fuel
    }

    // Copy old state into the overlap region
    int copyWidth = std::min(oldWidth, newWidth);
    int copyHeight = std::min(oldHeight, newHeight);

    for (int y = 0; y < copyHeight; y++) {
        for (int x = 0; x < copyWidth; x++) {
            int oldIdx = (y * oldWidth + x) * 4;
            int newIdx = (y * newWidth + x) * 4;
            newData[newIdx]     = oldData[oldIdx];
            newData[newIdx + 1] = oldData[oldIdx + 1];
            newData[newIdx + 2] = oldData[oldIdx + 2];
            newData[newIdx + 3] = oldData[oldIdx + 3];
        }
    }
    
    // Upload the new data
    glBindTexture(GL_TEXTURE_2D, newTex);
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, newWidth, newHeight, GL_RGBA, GL_FLOAT, newData.data());
}

// Global recording state variable
bool isRecording = false;
int recordingFrameRate = 30;
float frameInterval = 1.0f / 30.0f;  // Time between captured frames (1/30 second)
float timeSinceLastCapture = 0.0f;   // Time accumulator for frame capture

FILE* ffmpegPipe = nullptr;

void startFFmpegRecording() {
    // Get current date and time for filename
    auto now = std::chrono::system_clock::now();
    auto now_c = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    tm timeinfo;
    localtime_s(&timeinfo, &now_c);
    ss << "recording_" 
       << std::put_time(&timeinfo, "%Y-%m-%d_%H-%M-%S") 
       << ".mp4";
    std::string filename = ss.str();
    
    std::string ffmpegCommand = "ffmpeg -y -f rawvideo -vcodec rawvideo -pix_fmt rgba -s " + 
                               std::to_string(currentWidth) + "x" + std::to_string(currentHeight) + 
                               " -r " + std::to_string(recordingFrameRate) + " -i - -vf vflip -vcodec libx264 -crf 18 -preset fast " + 
                               filename;
    
    ffmpegPipe = _popen(ffmpegCommand.c_str(), "wb");
    if (!ffmpegPipe) {
        std::cerr << "Failed to open FFmpeg pipe." << std::endl;
        isRecording = false;
        return;
    }
    
    isRecording = true;
    timeSinceLastCapture = 0.0f;  // Reset the accumulator
    frameInterval = 1.0f / recordingFrameRate;  // Set interval based on target framerate
    
    std::cout << "Started recording to: " << filename << std::endl;
    std::cout << "Recording at " << recordingFrameRate << " FPS" << std::endl;
}

void stopFFmpegRecording() {
    if (ffmpegPipe) {
        _pclose(ffmpegPipe);
        ffmpegPipe = nullptr;
        isRecording = false;
        std::cout << "Recording stopped." << std::endl;
    }
}

void captureFrame() {
    if (!ffmpegPipe) return;

    std::vector<unsigned char> pixels(currentWidth * currentHeight * 4);
    glReadPixels(0, 0, currentWidth, currentHeight, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
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
    extern int currentWidth, currentHeight;
    ImGuiIO& io = ImGui::GetIO();
    if (io.WantCaptureMouse) {
        return;
    }

    if (isDragging) {
        double dx = xpos - lastMouseX;
        double dy = ypos - lastMouseY;

        // A screen delta in UV space / zoomFactor gives the world UV delta.
        // Subtract so the world follows the cursor (grab behaviour).
        // GLFW y increases downward; texture y increases upward — so dy sign is flipped.
        panX -= (float)(dx / currentWidth)  / zoomFactor;
        panY += (float)(dy / currentHeight) / zoomFactor;

        lastMouseX = xpos;
        lastMouseY = ypos;
    }
}

// Scroll callback for zooming
void scroll_callback(GLFWwindow* window, double xoffset, double yoffset) {
    extern int currentWidth, currentHeight;
    ImGuiIO& io = ImGui::GetIO();
    if (io.WantCaptureMouse) {
        return;
    }

    double mouseX, mouseY;
    glfwGetCursorPos(window, &mouseX, &mouseY);

    // Screen UV of the cursor (y flipped: GLFW y=0 is top, texture y=0 is bottom)
    float screenUV_x = (float)(mouseX / currentWidth);
    float screenUV_y = 1.0f - (float)(mouseY / currentHeight);

    // World UV currently under the cursor
    float worldUV_x = (screenUV_x - 0.5f) / zoomFactor + 0.5f + panX;
    float worldUV_y = (screenUV_y - 0.5f) / zoomFactor + 0.5f + panY;

    // Apply zoom
    zoomFactor *= (1.0f + (float)yoffset * mouseWheelSensitivity);
    zoomFactor = std::max(0.1f, std::min(zoomFactor, 20.0f));

    // Adjust pan so the cursor stays over the same world point
    panX = worldUV_x - (screenUV_x - 0.5f) / zoomFactor - 0.5f;
    panY = worldUV_y - (screenUV_y - 0.5f) / zoomFactor - 0.5f;
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
            panX = 0.0f;
            panY = 0.0f;
            zoomFactor = 1.0f;
        }
    } else {
        rKeyPressed = false;
    }

    // Toggle recording with 'P' key
    static bool pKeyPressed = false;
    if (glfwGetKey(window, GLFW_KEY_P) == GLFW_PRESS) {
        if (!pKeyPressed) {
            pKeyPressed = true;
            if (isRecording) {
                stopFFmpegRecording();
            } else {
                startFFmpegRecording();
            }
        }
    } else {
        pKeyPressed = false;
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

    // Shaders ../ because of CMake build directory structure
    simShader = createProgram("../shaders/pass_vert.glsl", "../shaders/rd_frag.glsl");
    visShader = createProgram("../shaders/pass_vert.glsl", "../shaders/rd_visual.glsl");

    setupQuad();

    // Initialize framebuffers with WIDTH and HEIGHT (will be resized on window resize)
    fbo1 = createFramebuffer(tex1, WIDTH, HEIGHT);
    fbo2 = createFramebuffer(tex2, WIDTH, HEIGHT);
    
    initState(tex1, WIDTH, HEIGHT);

    glUseProgram(simShader);
    glUniform2f(glGetUniformLocation(simShader, "dx"), 1.0f / WIDTH, 1.0f / HEIGHT);

    // Set the resolution uniform for both shaders
    glUseProgram(simShader);
    glUniform2f(glGetUniformLocation(simShader, "resolution"), (float)WIDTH, (float)HEIGHT);

    glUseProgram(visShader);
    glUniform2f(glGetUniformLocation(visShader, "resolution"), (float)WIDTH, (float)HEIGHT);

    // System 1 (cyan-blue) — "mitosis" parameters
    float feed  = 0.037f;
    float kill  = 0.060f;
    float diffU = 0.16f;
    float diffV = 0.08f;

    // System 2 (orange-red) — "coral" parameters
    float feed2 = 0.055f;
    float kill2 = 0.062f;
    float diffW = 0.14f;
    float diffX = 0.06f;

    float inhibit   = 1.1f; // cross-inhibition: activators suppress each other
    float crossfeed = 0.0f; // cross-feeding: V boosts W's fuel supply

    float dt = 0.1f;
    int stepsPerFrame = 1;

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
            
            ImGui::SliderInt("Steps/Frame", &stepsPerFrame, 1, 32);
            ImGui::SliderFloat("dt", &dt, 0.01f, 1.0f);

            if (ImGui::CollapsingHeader("System 1 (cyan-blue)", ImGuiTreeNodeFlags_DefaultOpen)) {
                ImGui::SliderFloat("Feed 1 (F)", &feed,  0.0f, 0.1f);
                ImGui::SliderFloat("Kill 1 (k)", &kill,  0.0f, 0.1f);
                ImGui::SliderFloat("Diff U",     &diffU, 0.0f, 1.0f);
                ImGui::SliderFloat("Diff V",     &diffV, 0.0f, 1.0f);
            }

            if (ImGui::CollapsingHeader("System 2 (orange-red)", ImGuiTreeNodeFlags_DefaultOpen)) {
                ImGui::SliderFloat("Feed 2 (F)", &feed2,  0.0f, 0.1f);
                ImGui::SliderFloat("Kill 2 (k)", &kill2,  0.0f, 0.1f);
                ImGui::SliderFloat("Diff W",     &diffW,  0.0f, 1.0f);
                ImGui::SliderFloat("Diff X",     &diffX,  0.0f, 1.0f);
            }

            if (ImGui::CollapsingHeader("Coupling", ImGuiTreeNodeFlags_DefaultOpen)) {
                ImGui::SliderFloat("Inhibition",  &inhibit,   0.0f, 3.0f);
                ImGui::SliderFloat("Cross-feed",  &crossfeed, 0.0f, 0.5f);
            }
            
            // Pan and zoom controls
            if (ImGui::CollapsingHeader("Pan & Zoom Controls", ImGuiTreeNodeFlags_DefaultOpen)) {
                ImGui::SliderFloat("Zoom", &zoomFactor, 0.1f, 20.0f);
                ImGui::SliderFloat("Pan X", &panX, -1.0f, 1.0f);
                ImGui::SliderFloat("Pan Y", &panY, -1.0f, 1.0f);
                ImGui::SliderFloat("Zoom Speed", &mouseWheelSensitivity, 0.01f, 0.5f);

                if (ImGui::Button("Reset Pan/Zoom")) {
                    panX = 0.0f;
                    panY = 0.0f;
                    zoomFactor = 1.0f;
                }
            }
            
            ImGui::End();
        }

        ImGui::Render();

        // Simulate: stepsPerFrame steps of tex1 -> tex2 -> tex1 -> ...
        glUseProgram(simShader);
        glUniform1f(glGetUniformLocation(simShader, "feed"),  feed);
        glUniform1f(glGetUniformLocation(simShader, "kill"),  kill);
        glUniform1f(glGetUniformLocation(simShader, "feed2"), feed2);
        glUniform1f(glGetUniformLocation(simShader, "kill2"), kill2);
        glUniform1f(glGetUniformLocation(simShader, "diffU"), diffU);
        glUniform1f(glGetUniformLocation(simShader, "diffV"), diffV);
        glUniform1f(glGetUniformLocation(simShader, "diffW"), diffW);
        glUniform1f(glGetUniformLocation(simShader, "diffX"), diffX);
        glUniform1f(glGetUniformLocation(simShader, "dt"),        dt);
        glUniform1f(glGetUniformLocation(simShader, "inhibit"),   inhibit);
        glUniform1f(glGetUniformLocation(simShader, "crossfeed"), crossfeed);
        glUniform1i(glGetUniformLocation(simShader, "currentState"), 0);

        glActiveTexture(GL_TEXTURE0);
        for (int step = 0; step < stepsPerFrame; ++step) {
            glBindFramebuffer(GL_FRAMEBUFFER, fbo2);
            glBindTexture(GL_TEXTURE_2D, tex1);
            renderQuad();
            std::swap(tex1, tex2);
            std::swap(fbo1, fbo2);
        }

        // Visualize: tex1 -> screen (tex1 holds the latest state after swaps)
        glUseProgram(visShader);
        // Pass pan and zoom uniforms to visualization shader
        glUniform1f(glGetUniformLocation(visShader, "zoomFactor"), zoomFactor);
        glUniform2f(glGetUniformLocation(visShader, "panOffset"), panX, panY);
        
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        glBindTexture(GL_TEXTURE_2D, tex1);
        glUniform1i(glGetUniformLocation(visShader, "stateTexture"), 0);
        renderQuad();

        // Render ImGui
        if (showUI) {
            ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
        }

        // Update FPS counter
        float currentTime = glfwGetTime();
        deltaTime = currentTime - lastTime; // Calculate deltaTime
        frameTime += deltaTime;
        lastTime = currentTime;
        frameCount++;

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

        // Capture frame for recording
        if (isRecording) {
            timeSinceLastCapture += deltaTime;
            if (timeSinceLastCapture >= frameInterval) {
                captureFrame();
                timeSinceLastCapture -= frameInterval; // Subtract interval instead of resetting to 0
                                                       // This maintains better timing accuracy for recordings
            }
        }

        // Ensure ImGui is rendered after all other OpenGL rendering
        glfwSwapBuffers(win);
    }

    // Cleanup ImGui
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();

    glfwTerminate();
    return 0;
}