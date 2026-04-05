#version 330 core

layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec2 TexCoords;

// Pan and zoom uniforms
uniform float zoomFactor = 1.0;
uniform vec2 panOffset = vec2(0.0, 0.0);

void main()
{
    // Apply pan and zoom to the texture coordinates
    TexCoords = (aTexCoord - 0.5) / zoomFactor + 0.5 - panOffset / zoomFactor;
    
    // Position remains unchanged (we're transforming the texture, not the screen)
    gl_Position = vec4(aPos.xy, 0.0, 1.0);
}