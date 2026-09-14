#version 150
uniform sampler2D Sampler0;
uniform vec4 ColorModulator;
uniform float SkyDay;
in vec2 texCoord0;
in vec4 vertexColor;
out vec4 fragColor;
void main() {
    vec2 uv = texCoord0;
    vec4 color = texture(Sampler0, uv);
    // A narrow shared colour bridge closes the wrap without reflecting clouds or stars.
    float edge = min(uv.x, 1.0 - uv.x);
    float seam = 1.0 - smoothstep(0.0, 0.025, edge);
    if (seam > 0.0) {
        vec4 boundary = 0.5 * (texture(Sampler0, vec2(0.0, uv.y))
                            + texture(Sampler0, vec2(1.0, uv.y)));
        color = mix(color, boundary, seam);
    }
    // Equirectangular poles must converge to a single colour, not stretched radial spokes.
    float pole = 1.0 - smoothstep(0.0, 0.065, min(uv.y, 1.0 - uv.y));
    if (pole > 0.0) {
        float v = uv.y < 0.5 ? 0.015 : 0.985;
        vec4 cap = (texture(Sampler0, vec2(0.125, v)) + texture(Sampler0, vec2(0.375, v))
                  + texture(Sampler0, vec2(0.625, v)) + texture(Sampler0, vec2(0.875, v))) * 0.25;
        color = mix(color, cap, pole);
    }
    // Aerial perspective pushes the horizon back and avoids an inverted cloud ceiling below islands.
    float horizon = 1.0 - smoothstep(0.0, 0.14, abs(uv.y - 0.5));
    vec3 haze = mix(vec3(0.018, 0.028, 0.065), vec3(0.48, 0.66, 0.82), SkyDay);
    color.rgb = mix(color.rgb, haze, horizon * mix(0.08, 0.22, SkyDay));
    float below = smoothstep(0.60, 0.96, uv.y);
    vec3 distanceColor = mix(vec3(0.008, 0.014, 0.035), vec3(0.16, 0.32, 0.52), SkyDay);
    color.rgb = mix(color.rgb, distanceColor, below * 0.85);
    // No alpha discard: even the first percent of dawn/healing must crossfade smoothly.
    fragColor = color * vertexColor * ColorModulator;
}
