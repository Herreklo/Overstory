// The sky, designed from the hour and the weather as a painter would build it: a dome lightest at the horizon and
// darkening to the zenith; the sun's glow tight round it and wide and low along the horizon on its side; the band
// opposite a low sun (the belt of Venus); a low cloud layer of big wind-stretched billows (the same field whose
// shadows lie on the town), its bellies darker, its edges silvered towards the sun, its undersides lit warm by a
// low sun and, at night, by the town's glow; a high thin layer that catches the sun after it has set for the town;
// and the low haze or fog bank towards the horizon, with the town's glow in it. The light rig sets every colour; the horizon matches the colour of the air (StreetSurface.hlsl,
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
                float2 dh = d.xz / max(length(d.xz), 1e-4);
                float2 sh = _OS_SunDir.xz / max(length(_OS_SunDir.xz), 1e-4);
                float towardsSun = dot(dh, sh) * 0.5 + 0.5;    // 1 at the sun's bearing, 0 opposite
                float low = exp(-max(d.y, 0.0) / 0.16);         // the band just over the horizon

                // the dome: lightest at the horizon, darkening to the zenith
                float t = pow(saturate(d.y), _Curve);
                if (_OS_SkyBands > 0.5)
                {
                    float tb = t * _OS_SkyBands;
                    t = (floor(tb) + smoothstep(0.7, 1.0, frac(tb))) / _OS_SkyBands;
                }
                half3 c = d.y >= 0 ? lerp(_Horizon.rgb, _Zenith.rgb, t)
                                   : lerp(_Horizon.rgb, _Below.rgb, saturate(-d.y * 6.0));
                // the sun's glow: tight round the sun, and wide and low along the horizon on its side
                c += _SunGlow.rgb * (pow(saturate(dot(d, _OS_SunDir.xyz)), max(_SunGlowPower, 1.0))
                                     + 0.55 * pow(towardsSun, 3.0) * low);
                // the band opposite a low sun (the belt of Venus), just over the horizon
                half band = (half)exp(-pow((d.y - 0.07) / 0.06, 2.0));
                c += _AntiGlow.rgb * (half)pow(1.0 - towardsSun, 3.0) * band;
                half3 sky = c;

                // the high layer: thin streaks along the wind, lit by the low sun's glow from below the town's horizon
                if (_HighCloud > 0.001 && d.y > 0.01)
                {
                    float2 p = _WorldSpaceCameraPos.xz + d.xz / d.y * (7000.0 - _WorldSpaceCameraPos.y);
                    float2 q = float2(dot(p, float2(0.866, 0.5)) / 3600.0, dot(p, float2(-0.5, 0.866)) / 480.0);
                    q += (float2(OS_Noise(q * 0.3 + 2.0), OS_Noise(q * 0.3 - 5.0)) - 0.5) * 0.8;
                    float f = 0.55 * OS_Noise(q) + 0.3 * OS_Noise(q * 2.3 + 4.1) + 0.15 * OS_Noise(q * 5.3 - 1.7);
                    half streak = (half)smoothstep(0.62 - _HighCloud * 0.2, 0.9 - _HighCloud * 0.1, f) * 0.55h;
                    half3 lit = _SunGlow.rgb * (0.7h + 0.9h * (half)towardsSun) + _Horizon.rgb * 0.5h;
                    c = lerp(c, lerp(c * 1.04h, lit, 0.7h), streak * (half)saturate(d.y * 9.0));
                }

                // the low layer: the same cloud whose shadows lie on the town
                if (_OS_Clouds.x > 0.001 && d.y > 0.004)
                {
                    float height = _OS_Clouds.w - _WorldSpaceCameraPos.y;
                    float2 p = _WorldSpaceCameraPos.xz + d.xz / d.y * height;
                    float field = OS_CloudField(p, 1.0);
                    half cover = OS_CloudCover(field, 0.04);
                    // how deep into the cloud: its belly darker
                    half thick = (half)saturate((field - (1.0 - _OS_Clouds.x)) / 0.3);
                    // an edge thinning towards the sun catches it: a silver lining
                    float towards = OS_CloudField(p + sh * _OS_Clouds.y * 0.12, 1.0);
                    half edge = (half)saturate(0.5 + (field - towards) * 6.0) * (1.0h - thick * 0.6h);
                    half sunUp = (half)saturate(_OS_SunDir.y * 6.0 + 0.3);
                    half3 shade = lerp(_Horizon.rgb, _Zenith.rgb, 0.45h) * lerp(0.98h, 0.6h, thick);
                    half3 sunlit = _OS_SunCol.rgb * (0.35h + 0.65h * edge) * sunUp;
                    // a low sun lights the undersides on its side warm; after it has set the glow lingers there
                    half lowSun = (half)saturate(1.0 - _OS_SunDir.y * 5.0);
                    half3 under = _SunGlow.rgb * (half)pow(towardsSun, 2.0) * lowSun * 0.8h;
                    // and over the town the fog's glow lights them from below
                    half3 townGlow = (half3)OS_GlowAt(float3(p.x, 0.0, p.y)) * 3.0h;
                    half3 cloud = shade * (1.0h - 0.35h * sunUp * edge) + sunlit * 0.8h + under + townGlow;
                    half far = (half)saturate(d.y * 7.0); // far clouds melt into the horizon's haze
                    c = lerp(c, cloud, cover * far);
                }

                // the low haze over the water, towards the horizon: what the town's own haze is, seen to its end
                if (_OS_Haze.x > 0.0)
                {
                    float H = max(_OS_Haze.y, 1.0);
                    float tau;
                    float3 glow = 0;
                    if (_OS_Bank.x > 0.5)
                        OS_HazeMarch(_WorldSpaceCameraPos, d, 3000.0, tau, glow); // the bank and the town's glow in it
                    else
                        tau = _OS_Haze.x * exp(-max(_WorldSpaceCameraPos.y, 0.0) / H) * H / max(d.y, 0.012);
                    half sun = (half)pow(saturate(dot(d, _OS_SunDir.xyz)), max(_OS_FogSun.w, 1.0));
                    c = lerp(c, _OS_HazeColor.rgb + _OS_FogSun.rgb * sun, (half)(1.0 - exp(-min(tau, 8.0)))) + (half3)glow;
                }
                return half4(c, 1);
            }
            ENDHLSL
        }
    }
}
