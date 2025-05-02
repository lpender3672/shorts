#version 330 core

in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D stateTexture;

void main()
{
    vec2 uv = texture(stateTexture, TexCoords).rg;
    float value = uv.y - uv.x;  // V - U

    // Bring it to visible range: usually around [-0.3, 0.3]
    value = value * 5.0 + 0.5;

    FragColor = vec4(vec3(clamp(value, 0.0, 1.0)), 1.0);
}