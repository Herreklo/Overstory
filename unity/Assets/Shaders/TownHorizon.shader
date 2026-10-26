// The town's horizon, worked out once from its sky map (Overstory.Scenes.SkyMap) for every metre of it, so a surface
// reads how much sky the town leaves it in a few taps instead of marching the map itself (StreetLooks.hlsl,
// OS_TownSky). Pass 0 writes, for one height over each texel's ground, the horizon's angle in four of eight
// directions; pass 1 writes that ground: the lowest open surface within a metre and a quarter, so the texels along a
// wall's foot count from the lane, not from the roof over them.
Shader "Hidden/Overstory/TownHorizon"
{
    SubShader
    {
        ZTest Always ZWrite Off Cull Off

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Common.hlsl"

        TEXTURE2D(_OS_SkyMap);
        SAMPLER(sampler_OS_SkyMap);
        float4 _OS_SkyMapRect;   // xy the map's corner (world x, z), z 1 / its size, w 1 when v reads from the top
        float4 _OS_HorizonInfo;  // x texels a side, y height levels, z the top level (m over the ground), w on
        float4 _OS_HorizonBuild; // x the height level drawn, y which four directions (0 or 1)

        struct Varyings { float4 positionCS : SV_POSITION; };

        Varyings Vert(uint id : SV_VertexID)
        {
            Varyings o;
            float2 uv = float2((id << 1) & 2, id & 2);
            o.positionCS = float4(uv * 2.0 - 1.0, 0.0, 1.0);
            return o;
        }

        float Height(float2 xz)
        {
            float2 q = (xz - _OS_SkyMapRect.xy) * _OS_SkyMapRect.z;
            q.y = _OS_SkyMapRect.w > 0.5 ? 1.0 - q.y : q.y;
            return SAMPLE_TEXTURE2D_LOD(_OS_SkyMap, sampler_OS_SkyMap, q, 0).r;
        }

        // the texel's middle in world x, z
        float2 Middle(float4 positionCS)
        {
            return _OS_SkyMapRect.xy + positionCS.xy / _OS_HorizonInfo.x / _OS_SkyMapRect.z;
        }

        // the lowest surface within 1.25 m; the sea and anything unmapped (cleared to -1000) count as sea level
        float Ground(float2 xz)
        {
            float g = 1e6;
            [unroll] for (int j = 0; j < 6; j++)
                [unroll] for (int i = 0; i < 6; i++)
                {
                    float h = Height(xz + (float2(i, j) - 2.5) * 0.5);
                    g = min(g, h < -500.0 ? 0.0 : h);
                }
            return g;
        }
        ENDHLSL

        Pass
        {
            Name "Horizon"
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            float4 Frag(Varyings input) : SV_Target
            {
                float2 xz = Middle(input.positionCS);
                float t = _OS_HorizonBuild.x / max(_OS_HorizonInfo.y - 1.0, 1.0);
                float y = Ground(xz) + _OS_HorizonInfo.z * t * t;
                const float reach[8] = { 1.0, 2.0, 3.5, 6.0, 10.0, 17.0, 30.0, 56.0 };
                float4 alpha = 0.0;
                [unroll] for (int k = 0; k < 4; k++)
                {
                    float a = (k + 4.0 * _OS_HorizonBuild.y + 0.5) * 0.785398;
                    float2 dir = float2(cos(a), sin(a));
                    float tanMax = 0.0;
                    [unroll] for (int j = 0; j < 8; j++)
                        tanMax = max(tanMax, (Height(xz + dir * reach[j]) - y - 0.2) / reach[j]);
                    alpha[k] = atan(tanMax) / HALF_PI;
                }
                return alpha;
            }
            ENDHLSL
        }

        Pass
        {
            Name "Ground"
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag

            float Frag(Varyings input) : SV_Target
            {
                return Ground(Middle(input.positionCS));
            }
            ENDHLSL
        }
    }
}
