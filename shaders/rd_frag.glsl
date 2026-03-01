#version 330 core

out vec4 FragColor;
in vec2 TexCoords;

uniform sampler2D currentState; // R=U, G=V (system 1)  B=W, A=X (system 2)
uniform vec2 dx;
uniform float feed,  kill;   // system 1
uniform float feed2, kill2;  // system 2
uniform float diffU, diffV, diffW, diffX;
uniform float dt;

// Coupling
uniform float inhibit;   // cross-inhibition: each activator suppresses the other's growth
uniform float crossfeed; // cross-feeding:    V boosts W's fuel supply (system 1 feeds system 2)

vec4 laplacian(vec4 centre) {
    vec4 sum = texture(currentState, TexCoords + vec2(-dx.x,  0.0))
             + texture(currentState, TexCoords + vec2( dx.x,  0.0))
             + texture(currentState, TexCoords + vec2(  0.0, -dx.y))
             + texture(currentState, TexCoords + vec2(  0.0,  dx.y));
    return sum - 4.0 * centre;
}

float rand(vec2 co) {
    return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

void main()
{
    vec4 s = texture(currentState, TexCoords);
    float u = s.r, v = s.g, w = s.b, x = s.a;

    // Continuous noise seeds to keep patterns alive
    if (length(TexCoords - vec2(0.50, 0.50)) < 0.012) {
        u += rand(TexCoords)        * 0.001;
        v += rand(TexCoords + 0.10) * 0.001;
    }
    if (length(TexCoords - vec2(0.33, 0.67)) < 0.012) {
        w += rand(TexCoords + 0.20) * 0.001;
        x += rand(TexCoords + 0.30) * 0.001;
    }

    vec4 lap = laplacian(s);

    float ruv = u * v * v;
    float rwx = w * x * x;

    // --- Coupling terms ---
    // Cross-inhibition: each activator directly kills the other
    float inhibit_v = inhibit * v * x;   // X suppresses V
    float inhibit_x = inhibit * x * v;   // V suppresses X

    // Cross-feeding: V's presence replenishes W's fuel.
    // System 1 "produces" something system 2 can consume.
    float boosted_feedW = feed2 + crossfeed * v;

    // --- Reaction-diffusion equations ---
    float du = diffU * lap.r - ruv + feed  * (1.0 - u);
    float dv = diffV * lap.g + ruv - (feed  + kill)  * v - inhibit_v;
    float dw = diffW * lap.b - rwx + boosted_feedW * (1.0 - w);
    float dx_ = diffX * lap.a + rwx - (feed2 + kill2) * x - inhibit_x;

    FragColor = vec4(u + du * dt,
                     v + dv * dt,
                     w + dw * dt,
                     x + dx_ * dt);
}
