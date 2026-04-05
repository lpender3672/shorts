#version 330 core

in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D stateTexture;
uniform float zoomFactor;
uniform vec2 panOffset;

void main()
{
    vec2 worldUV = (TexCoords - 0.5) / zoomFactor + 0.5 + panOffset;

    if (worldUV.x < 0.0 || worldUV.x > 1.0 || worldUV.y < 0.0 || worldUV.y > 1.0) {
        FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    vec4 s = texture(stateTexture, worldUV);

    float v_norm = clamp(s.g * 6.0, 0.0, 1.0);  // system 1 activator
    float x_norm = clamp(s.a * 6.0, 0.0, 1.0);  // system 2 activator

    // Where both activators coexist the boundary term flares bright yellow.
    // With inhibition active this is a thin, dynamic collision front.
    float boundary = v_norm * x_norm;

    vec3 col = v_norm   * vec3(0.05, 0.55, 1.00)   // cyan-blue   (system 1)
             + x_norm   * vec3(1.00, 0.35, 0.05)   // orange-red  (system 2)
             + boundary * vec3(1.00, 1.00, 0.20) * 2.5; // yellow boundary flash

    FragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
}
