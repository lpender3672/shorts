#version 330 core

out vec4 FragColor;
in vec2 TexCoords;

uniform sampler2D currentState; // Input texture: current state (R in .r, B in .g)
uniform vec2 dx;               // Grid spacing (normalized)
uniform float feed;             // Feed rate (F)
uniform float kill;             // Kill rate (k)
uniform float diffU;            // Diffusion rate of U (du)
uniform float diffV;            // Diffusion rate of V (dv)
uniform float dt;               // Time step
uniform float zoomFactor = 1.0; // Zoom factor (default: 1.0)
uniform vec2 panOffset = vec2(0.0, 0.0); // Pan offset (default: 0, 0)

// Adjusted laplacian function for pan/zoom
vec2 laplacian(vec2 uv) {
    // We need to adjust the sampling offsets to account for zoom factor
    vec2 adjustedDx = dx / zoomFactor;
    
    vec2 sum = vec2(0.0);
    sum += texture(currentState, TexCoords + vec2(-adjustedDx.x, 0.0)).rg;
    sum += texture(currentState, TexCoords + vec2(adjustedDx.x, 0.0)).rg;
    sum += texture(currentState, TexCoords + vec2(0.0, -adjustedDx.y)).rg;
    sum += texture(currentState, TexCoords + vec2(0.0, adjustedDx.y)).rg;
    sum -= 4.0 * uv;
    return sum;
}

float rand(vec2 co) {
    return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

void main()
{
    // Check if we're sampling outside the [0,1] range and clamp if needed
    if (TexCoords.x < 0.0 || TexCoords.x > 1.0 || TexCoords.y < 0.0 || TexCoords.y > 1.0) {
        FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    vec2 uv = texture(currentState, TexCoords).rg; // U in r, V in g

    // Convert texture coordinates to world coordinates for noise application
    vec2 worldCoords = (TexCoords - 0.5) * zoomFactor + 0.5;
    
    // Add random noise only if within a circle of unit radius
    if (length(worldCoords - vec2(0.5)) <= 0.01) {
        uv += vec2(rand(worldCoords), rand(worldCoords)) * 0.001;
    }

    vec2 lap = laplacian(uv);

    float u = uv.x;
    float v = uv.y;

    float reaction = u * v * v;

    float du = diffU * lap.x - reaction + feed * (1.0 - u);
    float dv = diffV * lap.y + reaction - (feed + kill) * v;

    u += du * dt;
    v += dv * dt;

    FragColor = vec4(u, v, 0.0, 1.0); // Store U in red, V in green
}