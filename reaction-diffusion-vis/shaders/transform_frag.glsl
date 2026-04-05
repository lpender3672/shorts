#version 330 core

out vec4 FragColor;
in vec2 TexCoords;

uniform sampler2D inputTexture;
uniform float oldZoom;
uniform float newZoom;
uniform vec2 oldPan;
uniform vec2 newPan;

void main()
{
    // Convert current NDC coordinates [0,1] to world space using new transform params
    vec2 worldPos = (TexCoords - 0.5) / newZoom + 0.5 - newPan / newZoom;
    
    // Convert world pos back to NDC using old transform params
    vec2 oldTexCoords = (worldPos + oldPan / oldZoom - 0.5) * oldZoom + 0.5;
    
    // Sample input texture with the transformed coordinates
    if(oldTexCoords.x >= 0.0 && oldTexCoords.x <= 1.0 && 
       oldTexCoords.y >= 0.0 && oldTexCoords.y <= 1.0) {
        FragColor = texture(inputTexture, oldTexCoords);
    } else {
        FragColor = vec4(0.0, 0.0, 0.0, 1.0); // Out of bounds
    }
}