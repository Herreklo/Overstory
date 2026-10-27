// The painted corner's air (LT1ArtPasses.Paint): one full-screen pass over the surfaces' colour and their distance
// from the eye (PaintSurface.shader, _P_Mode 1: r the distance times the coverage, g the coverage). It draws the sky
// where nothing stands, the sea fog in three stepped layers by distance (the near clear, the Landing veiled, the far
// town a flat shape in the fog's colour), each lamp's tight halo where nothing stands before it, and the grade (a soft
// shoulder for the hot heads, a vignette). In the game it is one full-screen pass on the depth buffer; here it reads
// the distance pass so the edges against the sky stay clean through the anti-aliasing. Every value is from Paint.json.
Shader "Hidden/Overstory/PaintAir"
{
    Properties
    {
        _MainTex ("Colour", 2D) = "black" {}
        _P_Dist ("Distance, coverage", 2D) = "black" {}
    }

    SubShader
    {
        ZTest Always Cull Off ZWrite Off

        Pass
        {
            CGPROGRAM
            #pragma target 4.5
            #pragma vertex vert_img
            #pragma fragment Frag
            #include "UnityCG.cginc"
            #include "Paint.hlsl"

            sampler2D _MainTex;
            sampler2D _P_Dist;
            float4 _P_CamPos, _P_CamFwd, _P_CamRight, _P_CamUp;   // right and up scaled by the half view's tangent
            float4 _P_FogD, _P_FogW, _P_FogA;
            float4 _P_Grade;                                        // x vignette, y exposure, z the shoulder's start
            float4 _P_HaloShape;                                    // x the wide part's share, y the depth margin (m)
            float4 _P_LampPos[8];                                   // xyz the head (world), w the core's radius (m)
            float4 _P_LampHalo[8];                                  // rgb its light, w the wide part's radius (m)
            float _P_LampCount;

            float Step(float d, float at, float w)
            {
                return smoothstep(at - w, at + w, d);
            }

            float3 Shoulder(float3 x, float k)
            {
                float3 over = max(x - k, 0.0);
                float s = max(1.0 - k, 1e-3);
                return min(x, k) + s * (1.0 - exp(-over / s));
            }

            float4 Frag(v2f_img i) : SV_Target
            {
                float2 uv = i.uv;
                float3 colour = tex2D(_MainTex, uv).rgb;
                float3 dc = tex2D(_P_Dist, uv).rgb;
                float c = saturate(dc.y);
                float d = c > 1e-3 ? dc.x / c : 0.0;
                float veil = c > 1e-3 ? dc.z / c : 1.0;
                float3 dir = normalize(_P_CamFwd.xyz + (uv.x * 2.0 - 1.0) * _P_CamRight.xyz + (uv.y * 2.0 - 1.0) * _P_CamUp.xyz);

                // the sky where nothing stands; the fog's layers over what does
                float3 sky = P_Sky(dir);
                float3 surf = c > 1e-3 ? colour / c : 0.0;
                float a = _P_FogA.x + veil * (
                      (_P_FogA.y - _P_FogA.x) * Step(d, _P_FogD.x, _P_FogW.x)
                    + (_P_FogA.z - _P_FogA.y) * Step(d, _P_FogD.y, _P_FogW.y)
                    + (_P_FogA.w - _P_FogA.z) * Step(d, _P_FogD.z, _P_FogW.z));
                float3 fogged = lerp(surf, P_Fog(dir), saturate(a));
                float3 result = c * fogged + (1.0 - c) * sky;

                // each lamp's halo: a tight core and a little of a wider glow, hidden by what stands before the head
                float3 halo = 0.0;
                for (int k = 0; k < (int)_P_LampCount; k++)
                {
                    float3 L = _P_LampPos[k].xyz - _P_CamPos.xyz;
                    float ld = length(L);
                    float t = dot(L, dir);
                    if (t <= 0.0)
                        continue;
                    float x = length(L - t * dir);
                    float m = max(_P_HaloShape.y, 0.05);
                    float vis = lerp(1.0, saturate((d - ld + m) / m), c);
                    float core = max(_P_LampPos[k].w, 1e-3), wide = max(_P_LampHalo[k].w, 1e-3);
                    float g = exp(-(x * x) / (core * core)) + _P_HaloShape.x * exp(-(x * x) / (wide * wide));
                    halo += _P_LampHalo[k].rgb * (g * vis);
                }
                result += halo;

                result *= _P_Grade.y;
                result = Shoulder(result, _P_Grade.z);
                float2 q = (uv - 0.5) * 2.0;
                result *= 1.0 - _P_Grade.x * saturate(dot(q, q) * 0.5);
                return float4(result, 1.0);
            }
            ENDCG
        }
    }
}
