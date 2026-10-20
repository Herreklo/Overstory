// The house style's colour, applied after the grade (Overstory.Scenes.Style; docs/research/masters-of-colour.md):
// values pulled softly into a few masses; a designed ramp of colour by value blended over the scene with the light
// kept, sparing saturated colour so a lit window stays warm and a sign keeps its red; colour added in the middle
// values and rolled off towards black and white, as print film does. Off when no style is set.
Shader "Overstory/Palette"
{
    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" }
        ZWrite Off
        ZTest Always
        Cull Off

        Pass
        {
            Name "Palette"

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Color.hlsl"

            float _OS_PaletteOn;
            float4 _OS_Key0, _OS_Key1, _OS_Key2, _OS_Key3; // the ramp's colours (perceptual, sRGB), dark to light
            float4 _OS_PaletteParams;                      // x ramp strength, y spare saturated, z vibrance, w roll-off
            float4 _OS_Grouping;                           // x steps, y strength, z softness

            float Luma(float3 g) { return dot(g, float3(0.2126, 0.7152, 0.0722)); }

            float3 Ramp(float v)
            {
                float t = saturate(v) * 3.0;
                if (t < 1.0) return lerp(_OS_Key0.rgb, _OS_Key1.rgb, t);
                if (t < 2.0) return lerp(_OS_Key1.rgb, _OS_Key2.rgb, t - 1.0);
                return lerp(_OS_Key2.rgb, _OS_Key3.rgb, t - 2.0);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 colour = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, input.texcoord);
                if (_OS_PaletteOn < 0.5)
                    return colour;
                // work in perceptual values, as a painter mixes
                float3 g = LinearToSRGB(saturate(colour.rgb));
                float v = Luma(g);

                // values in masses: a soft pull towards a few steps
                if (_OS_Grouping.x > 0.5 && _OS_Grouping.y > 0.0)
                {
                    float n = _OS_Grouping.x;
                    float f = frac(v * n);
                    float w = max(_OS_Grouping.z, 0.02) * 0.5;
                    float q = (floor(v * n) + smoothstep(0.5 - w, 0.5 + w, f)) / n;
                    float v2 = lerp(v, q, _OS_Grouping.y);
                    g *= v2 / max(v, 1e-4);
                    v = v2;
                }

                // colour by value: the ramp's hue and chroma at this value, at this value's lightness
                float hi = max(g.r, max(g.g, g.b)), lo = min(g.r, min(g.g, g.b));
                float sat = (hi - lo) / max(hi, 1e-4);
                float amount = _OS_PaletteParams.x * (1.0 - _OS_PaletteParams.y * smoothstep(0.35, 0.75, sat * smoothstep(0.25, 0.6, v)));
                float3 r = Ramp(v);
                r *= v / max(Luma(r), 1e-4);
                g = lerp(g, r, amount);

                // colour richest in the middle values, falling away towards black and white
                float grey = Luma(g);
                float3 chroma = g - grey;
                float middle = saturate(4.0 * grey * (1.0 - grey));
                chroma *= (1.0 + _OS_PaletteParams.z * middle) * (1.0 - _OS_PaletteParams.w * (1.0 - middle));
                g = grey + chroma;

                colour.rgb = SRGBToLinear(saturate(g));
                return colour;
            }
            ENDHLSL
        }
    }
}
