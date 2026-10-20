// The sky: a gradient from the horizon to the zenith, the ground's colour below the horizon, a glow towards the
// sun and a band opposite a low sun (the belt of Venus); a low broken cloud layer, the same pattern whose shadows
// lie on the town, and a high thin one that catches the sun after it has set for the town; and the low haze over
// the water. The light rig sets every colour; the horizon matches the colour of the air (StreetSurface.hlsl,
// OS_Atmosphere) so distant things fade into the sky they stand against.
Shader "Overstory/Sky"
{
    Properties
    {
        _Zenith ("Zenith", Color) = (0.55, 0.6, 0.66, 1)
        _Horizon ("Horizon", Color) = (0.7, 0.73, 0.76, 1)
        _Below ("Below the horizon", Color) = (0.3, 0.32, 0.32, 1)
        _Curve ("Gradient curve", Range(0.2, 4)) = 0.6
        _SunGlow ("Sun glow", Color) = (0, 0, 0, 1)
        _SunGlowPower ("Sun glow tightness", Float) = 8
        _AntiGlow ("Glow opposite the sun", Color) = (0, 0, 0, 1)
        _HighCloud ("High cloud", Range(0, 1)) = 0
    }

    SubShader
    {
        Tags { "Queue" = "Background" "RenderType" = "Background" "PreviewType" = "Skybox" "RenderPipeline" = "UniversalPipeline" }
        Cull Off
        ZWrite Off

        Pass
        {
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "StreetSurface.hlsl" // the shared cloud layer: the clouds here cast the shadows on the town

            CBUFFER_START(UnityPerMaterial)
                half4 _Zenith, _Horizon, _Below, _SunGlow, _AntiGlow;
                half _Curve, _SunGlowPower, _HighCloud;
            CBUFFER_END
            float _OS_SkyBands;
            float4 _OS_SunCol; // the sun's light (linear), for the clouds' lit sides // 0: a smooth gradient; n: n graded bands, the printer's bokashi (look D)

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 dir : TEXCOORD0; };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                o.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                o.dir = input.positionOS.xyz;
                return o;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float3 d = normalize(input.dir);
                float t = pow(saturate(d.y), _Curve);
                if (_OS_SkyBands > 0.5)
                {
                    float tb = t * _OS_SkyBands;
                    t = (floor(tb) + smoothstep(0.7, 1.0, frac(tb))) / _OS_SkyBands;
                }
                half3 c = d.y >= 0 ? lerp(_Horizon.rgb, _Zenith.rgb, t)
                                   : lerp(_Horizon.rgb, _Below.rgb, saturate(-d.y * 6.0));
                c += _SunGlow.rgb * pow(saturate(dot(d, _OS_SunDir.xyz)), max(_SunGlowPower, 1.0));
                float2 dh = d.xz / max(length(d.xz), 1e-4);
                float2 sh = _OS_SunDir.xz / max(length(_OS_SunDir.xz), 1e-4);
                half opposite = (half)pow(saturate(-dot(dh, sh) * 0.5 + 0.5), 3.0);
                half band = (half)exp(-pow((d.y - 0.07) / 0.06, 2.0));
                c += _AntiGlow.rgb * opposite * band;

                // the high layer: thin streaks along the wind, lit by the low sun's glow from below the town's horizon
                if (_HighCloud > 0.001 && d.y > 0.01)
                {
                    float2 p = _WorldSpaceCameraPos.xz + d.xz / d.y * (7000.0 - _WorldSpaceCameraPos.y);
                    float2 q = float2(dot(p, float2(0.866, 0.5)) / 3200.0, dot(p, float2(-0.5, 0.866)) / 520.0);
                    float f = 0.55 * OS_Noise(q) + 0.3 * OS_Noise(q * 2.3 + 4.1) + 0.15 * OS_Noise(q * 5.3 - 1.7);
                    half streak = (half)smoothstep(0.78 - _HighCloud * 0.35, 0.98 - _HighCloud * 0.2, f) * 0.6h;
                    half sunward = (half)pow(saturate(dot(d, _OS_SunDir.xyz) * 0.5 + 0.5), 2.0);
                    half3 lit = _SunGlow.rgb * (0.9h + 0.8h * sunward) + _Horizon.rgb * 0.45h;
                    c = lerp(c, lerp(c * 1.06h, lit, 0.75h), streak * saturate(d.y * 9.0));
                }

                // the clouds: the view ray meets the cloud layer, the same pattern whose shadows lie on the town
                if (_OS_Clouds.x > 0.001 && d.y > 0.004)
                {
                    float height = _OS_Clouds.w - _WorldSpaceCameraPos.y;
                    float2 p = _WorldSpaceCameraPos.xz + d.xz / d.y * height;
                    float field = OS_CloudField(p, 1.0);
                    half cover = OS_CloudCover(field, 0.07);
                    // an edge is lit where the cloud thins towards the sun, shaded where it thickens
                    float2 toSun = normalize(_OS_SunDir.xz + float2(1e-4, 0));
                    float towards = OS_CloudField(p + toSun * _OS_Clouds.y * 0.22, 1.0);
                    half lit = saturate(0.45h + (half)(field - towards) * 7.0h);
                    if (_OS_SkyBands > 0.5)
                        lit = (floor(lit * 3.0h) + smoothstep(0.75h, 1.0h, frac(lit * 3.0h))) / 3.0h; // in plates, as look D cuts all light
                    half3 shade = lerp(_Horizon.rgb, _Zenith.rgb, 0.4h) * 0.82h;     // a cloud's shade is the sky's colour
                    half3 sunlit = _OS_SunCol.rgb + _Horizon.rgb * 0.35h;
                    half3 cloud = lerp(shade, sunlit, lit * lit);
                    half far = saturate(d.y * 7.0); // far clouds melt into the horizon's haze
                    c = lerp(c, cloud, cover * far);
                }

                // the low haze over the water, towards the horizon: what the town's own haze is, seen to its end
                if (_OS_Haze.x > 0.0)
                {
                    float H = max(_OS_Haze.y, 1.0);
                    float tau = _OS_Haze.x * exp(-max(_WorldSpaceCameraPos.y, 0.0) / H) * H / max(d.y, 0.012);
                    half sun = (half)pow(saturate(dot(d, _OS_SunDir.xyz)), max(_OS_FogSun.w, 1.0));
                    c = lerp(c, _OS_HazeColor.rgb + _OS_FogSun.rgb * sun, (half)(1.0 - exp(-min(tau, 8.0))));
                }
                return half4(c, 1);
            }
            ENDHLSL
        }
    }
}
