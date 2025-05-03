#version 430 core

// Define work group size
layout (local_size_x = 16, local_size_y = 16) in;

// Input and output images (binding points will be set in the C++ code)
layout (binding = 0, rgba32f) uniform image2D inputState;
layout (binding = 1, rgba32f) uniform image2D outputState;

// Parameters (same as in fragment shader)
uniform float feed;
uniform float kill;
uniform float diffU;
uniform float diffV;
uniform float dt;
uniform vec2 resolution;

void main() {
    // Get current pixel coordinates (global ID corresponds to the pixel being processed)
    ivec2 pixel = ivec2(gl_GlobalInvocationID.xy);
    
    // Get dimensions of image
    ivec2 dimensions = imageSize(inputState);
    
    // Skip if outside bounds
    if (pixel.x >= dimensions.x || pixel.y >= dimensions.y)
        return;
    
    // Calculate dx based on resolution
    vec2 dx = vec2(1.0) / resolution;
    
    // Sample current state and neighbors
    vec4 center = imageLoad(inputState, pixel);
    vec4 left = imageLoad(inputState, ivec2(max(0, pixel.x-1), pixel.y));
    vec4 right = imageLoad(inputState, ivec2(min(dimensions.x-1, pixel.x+1), pixel.y));
    vec4 top = imageLoad(inputState, ivec2(pixel.x, max(0, pixel.y-1)));
    vec4 bottom = imageLoad(inputState, ivec2(pixel.x, min(dimensions.y-1, pixel.y+1)));
    
    // Extract U and V values
    float u = center.r;
    float v = center.g;
    
    // Calculate Laplacian (this approximation matches your fragment shader approach)
    float lapU = left.r + right.r + top.r + bottom.r - 4.0 * u;
    float lapV = left.g + right.g + top.g + bottom.g - 4.0 * v;
    
    // Apply Gray-Scott reaction-diffusion formula
    float du = diffU * lapU - u * v * v + feed * (1.0 - u);
    float dv = diffV * lapV + u * v * v - (feed + kill) * v;
    
    // Update state
    float newU = u + dt * du;
    float newV = v + dt * dv;
    
    // Write result to output image
    imageStore(outputState, pixel, vec4(newU, newV, 0.0, 1.0));
}