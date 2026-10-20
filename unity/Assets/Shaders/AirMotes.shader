// Motes in the air: dust in sunbeams by day, droplets of mist round the lamps at night (Overstory.Scenes.AirMotes).
// Each is a tiny soft disc facing the camera, lit only where light reaches it: by the sun through its shadow map and
// the cloud (so motes sparkle inside a beam and vanish in shade) and by the town's lamps; light scatters forward, so
// motes glow looking towards a light. They fade with distance and with the air in front of them, and are never
// smaller than about a pixel, so they do not shimmer. Positions are seeded and wrap round the camera, so a still is
// repeatable and the air never runs out as the camera moves.
Shader "Overstory/AirMotes"
{
    SubShader
    {
        Tags { "Queue" = "Transparent" "RenderType" = "Transparent" "RenderPipeline" = "UniversalPipeline" "IgnoreProjector" = "True" }

        Pass
        {
            Name "Motes"
            Tags { "LightMode" = "UniversalForward" }
            Blend One One
            ZWrite Off
            ZTest LEqual
            Cull Off

            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 4.5
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile _ _ADDITIONAL_LIGHTS
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "StreetSurface.hlsl"

            float4 _OS_Motes;      // x brightness (0 off), y box size (m), z mote size (m), w how far they show (m)
            float4 _OS_MoteSun;    // x forward scattering g, y how much the sun lights them, z how much the lamps do

            struct Attributes
            {
                float3 positionOS : POSITION;   // the mote's place in the box (0 to 1 on each axis)
                float2 corner : TEXCOORD0;      // -1 to 1
                float2 seed : TEXCOORD1;        // x a random 0-1, y its size factor
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 corner : TEXCOORD0;
                float3 centreWS : TEXCOORD1;
                half fade : TEXCOORD2;
            };

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                float box = _OS_Motes.y;
                float3 cam = _WorldSpaceCameraPos;
                // the box wraps round the camera: each mote is always somewhere within half a box of it
                float3 local = frac(input.positionOS - cam / box) - 0.5;
                float3 centre = cam + local * box;
                float dist = length(centre - cam);
                float size = _OS_Motes.z * input.seed.y;
                // never smaller than about one and a half pixels, so it does not shimmer; dimmer instead
                float pixel = dist * 2.0 / (_ScreenParams.y * UNITY_MATRIX_P._m11);
                float grown = max(size, pixel * 1.5);
                float3 right = UNITY_MATRIX_V[0].xyz, up = UNITY_MATRIX_V[1].xyz;
                float3 p = centre + (right * input.corner.x + up * input.corner.y) * grown;
                o.positionCS = TransformWorldToHClip(p);
                o.corner = input.corner;
                o.centreWS = centre;
                o.fade = (half)(saturate(1.0 - dist / _OS_Motes.w) * saturate(dist / 0.6) * (size * size) / (grown * grown));
                return o;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                if (_OS_Motes.x <= 0.0)
                    return 0;
                half disc = saturate(1.0h - (half)dot(input.corner, input.corner));
                disc *= disc;
                float3 c = input.centreWS;
                float3 v = normalize(c - _WorldSpaceCameraPos);
                float g = _OS_MoteSun.x, g2 = g * g;

                // the sun, where it reaches the mote
                Light sun = GetMainLight(TransformWorldToShadowCoord(c));
                float mu = dot(v, sun.direction);
                float hg = (1.0 - g2) / pow(max(1.0 + g2 - 2.0 * g * mu, 1e-4), 1.5);
                half3 light = sun.color * sun.shadowAttenuation * (half)(hg * _OS_MoteSun.y);

                // the lamps near it
            #if defined(_ADDITIONAL_LIGHTS)
                InputData inputData = (InputData)0;
                inputData.positionWS = c;
                inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(input.positionCS);
                half4 shadowMask = half4(1, 1, 1, 1);
                uint count = GetAdditionalLightsCount();
                LIGHT_LOOP_BEGIN(count)
                    Light l = GetAdditionalLight(lightIndex, c, shadowMask);
                    float ml = dot(v, l.direction);
                    float hl = (1.0 - g2) / pow(max(1.0 + g2 - 2.0 * g * ml, 1e-4), 1.5);
                    light += l.color * l.distanceAttenuation * (half)(hl * _OS_MoteSun.z);
                LIGHT_LOOP_END
            #endif

                // the air in front of it takes its share, as it does from everything else
                half3 seen = OS_Atmosphere(light, c) - OS_Atmosphere(0, c);
                return half4(seen * (disc * input.fade * _OS_Motes.x), 0);
            }
            ENDHLSL
        }
    }
}
