#ifndef OVERSTORY_GROWTH_PAINT_INCLUDED
#define OVERSTORY_GROWTH_PAINT_INCLUDED

// Growth in the painted corner (the art-direction page, The growth): lichen and moss over a rock's or a stone's albedo,
// as the page draws them. Lichen is flat crusts that follow the rock, matte, a few big shapes per face, lighter than
// the rock by at most 5 L* at blue hour, never mounds: so no height, no rim, no specks. Moss is a darker, greener
// pigment where the bake puts it (a joint, a damp foot, a low north face). Broad shapes, never noise: the big crusts
// are the shapes and hold past the focus; their lobed edges and the small crusts are the marks, shown near the focus
// and gone past it (the page: marks gone past 12 m, shapes held), the edges softening as they go; once a pixel covers
// much of a crust, it is seen as its mean.
//
// Where and for how long are the surface's facts, baked by its generator (blender/generators/growth.py: on_rock, and
// the stones' own bake): UV4.y the lichen's years / 200, UV5.x the moss. Its values are the setting pack's
// (packs/<pack>/growth.json, painted), set as globals by the growth's own code. Self-contained: nothing else to include.
//
// Called by the growth's own overlay (Shaders/GrowthOverlay.shader).

float4 _GP_Lichen;        // rgb the crust's albedo over its rock's, w the share a quiet century covers
float4 _GP_LichenShape;   // x the big colonies' spacing (m), y the small ones', z the lobes' size (m), w how far they bite (of a radius)
float4 _GP_LichenSoft;    // x the edge's softness (of a spacing), y the clusters' size (m), z the years / 200 at which the share is reached, w how much the clusters vary the share
float4 _GP_Moss;          // rgb the moss's albedo over its stone's, w its shapes' size (m)
float4 _GP_MossSoft;      // x its edge's softness, y the small colonies' share of the lichen
float4 _GP_LichenFar;     // x the crusts' edge past the focus (of a spacing), y z the big crusts' own lobes (size m, how far they bite, of a cell), w how sharply the clusters part (0 to 1)

float GP_Hash(float2 p)
{
    float3 p3 = frac(float3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return frac((p3.x + p3.y) * p3.z);
}

float4 GP_Hash4(float2 p)
{
    float4 p4 = frac(float4(p.xyxy) * float4(0.1031, 0.1030, 0.0973, 0.1099));
    p4 += dot(p4, p4.wzxy + 33.33);
    return frac((p4.xxyz + p4.yzzw) * p4.zywx);
}

float GP_Noise(float2 p)
{
    float2 i = floor(p), f = frac(p);
    float2 u = f * f * (3.0 - 2.0 * f);
    float a = GP_Hash(i), b = GP_Hash(i + float2(1, 0)), c = GP_Hash(i + float2(0, 1)), d = GP_Hash(i + float2(1, 1));
    return lerp(lerp(a, b, u.x), lerp(c, d, u.x), u.y);
}

// The share where a colony took (qc, m in the face's plane): the face's potential P carried there along its gradient
// gP (per m, from the screen derivatives) and the clusters' own there. A colony takes or not, and grows, by its own
// place, so it is always whole: never cut along the contours of a potential that changes across it.
float GP_ShareAt(float2 qc, float P, float2 gP, float2 q)
{
    float s = saturate(P + dot(gP, qc - q));
    float cl = GP_Noise(qc / max(_GP_LichenSoft.y, 0.1) + 3.1);
    cl = lerp(cl, smoothstep(0.25, 0.75, cl), _GP_LichenFar.w);
    return saturate(s * (1.0 + _GP_LichenSoft.w * (cl - 0.5) * 2.0));
}

// The big colonies' and the small ones' shares of a share: the small take part of it, the big the rest (their union
// is the share).
float2 GP_Split(float share, float part)
{
    float sSmall = share * part;
    return float2(1.0 - (1.0 - share) / max(1.0 - sSmall, 1e-3), sSmall);
}

// One size of colonies: a crust grows out from where it took, so each is a disc with a lobed edge, and where they
// crowd they merge into a scalloped patch (never the swirl of a noise field). In cells of spacing c (m): each cell's
// colony took (by the share at its place) at a seeded place with a seeded size; the share sets how many took and how
// far they have grown (a fit of the union's cover: 0.34 of the face when all have taken at full size; it holds with
// the reach capped). part: the small colonies' part of the share; which: 0 the big, 1 the small. lobe: the edge's
// bite here (in cells); aa: the edge's softness (in cells). Returns the cover, 0 to 1.
float GP_Colonies(float2 q, float c, float P, float2 gP, float part, int which, float lobe, float aa, float seed)
{
    float2 g = q / c;
    float2 i = floor(g);
    float cover = 0.0;
    [unroll] for (int y = -1; y <= 1; y++)
    [unroll] for (int x = -1; x <= 1; x++)
    {
        float2 cell = i + float2(x, y);
        float4 h = GP_Hash4(cell + seed);
        float s = saturate(GP_Split(GP_ShareAt((cell + h.xy) * c, P, gP, q), part)[which]);
        float took = saturate(s / 0.34);
        float grown = max(1.0, sqrt(-log(max(1.0 - s, 1e-3)) / 0.44));
        // (a colony reaches at most a cell from where it took, or the 3x3 search would cut it straight: where they
        // crowd, their neighbours fill in)
        float rho = min(lerp(0.18, 0.62, h.z * h.z) * grown, 1.0 - aa - abs(lobe));
        float d = distance(g, cell + h.xy) + lobe;
        float k = (h.w < took ? 1.0 : 0.0) * (1.0 - smoothstep(rho - aa, rho + aa, d));
        cover = max(cover, k);
    }
    return cover;
}

// x the lichen's cover, y the moss's, over a face: lichen (years / 200), moss (0 to 1), q its own plane (m), detail (1
// near the focus, 0 past it), footprint (m a pixel covers). The big crusts are shapes and hold at every distance until
// one spans only a few pixels, when it is seen as its share; the small crusts and the lobes are marks, gone past the
// focus (their share given to the big), and the edges soften there: a broad value shift, never specks.
float2 GP_GrowthCover(float lichen, float moss, float2 q, half detail, float footprint)
{
    // no branches: the edges' widths and the potential's gradient come from screen derivatives, which need every
    // pixel of a quad
    float d = (float)detail;
    float P = _GP_Lichen.w * saturate(lichen / max(_GP_LichenSoft.z, 1e-3));
    float2 dqx = ddx(q), dqy = ddy(q);
    float dPx = ddx(P), dPy = ddy(P);
    float det = dqx.x * dqy.y - dqx.y * dqy.x;
    float2 gP = abs(det) > 1e-12 ? float2(dPx * dqy.y - dPy * dqx.y, dPy * dqx.x - dPx * dqy.x) / det : 0.0;
    gP *= min(1.0, 0.5 / max(length(gP), 1e-6));   // (a facet's edge or a grazing view: no wild slopes)
    float part = _GP_MossSoft.y * d;   // the small colonies are marks, gone past the focus
    float lobe = (GP_Noise(q / max(_GP_LichenShape.z, 0.005)) - 0.5) * _GP_LichenShape.w * 0.5 * d;
    // the big crusts' own outline (a shape, held at every distance): never a circle
    float outline = (GP_Noise(q / max(_GP_LichenFar.y, 0.01) + 5.3) - 0.5) * _GP_LichenFar.z;
    float cBig = _GP_LichenShape.x, cSmall = _GP_LichenShape.y;
    float soft = lerp(_GP_LichenFar.x, _GP_LichenSoft.x, d);
    float big = GP_Colonies(q, cBig, P, gP, part, 0, lobe + outline, max(soft, footprint / cBig), 0.0);
    float small = GP_Colonies(q, cSmall, P, gP, part, 1, lobe, max(_GP_LichenSoft.x, footprint / cSmall), 17.0);
    // seen as its share once a colony spans only a few pixels
    float2 mean = GP_Split(GP_ShareAt(q, P, gP, q), part);
    big = lerp(big, mean.x, saturate(footprint / (cBig * 0.08) - 1.0));
    small = lerp(small, mean.y, saturate(footprint / (cSmall * 0.08) - 1.0));
    float2 cover;
    cover.x = 1.0 - (1.0 - big) * (1.0 - small);

    float g = GP_Noise(q / max(_GP_Moss.w, 0.01) + 7.7);
    float m = moss * (0.7 + 0.6 * g);
    float aam = max(_GP_MossSoft.x, fwidth(m));
    cover.y = smoothstep(0.35 - aam, 0.35 + aam, m) * saturate(moss * 2.0);
    return cover;
}

// The albedo's ratio the growth makes (multiply the surface's albedo by it).
half3 GP_GrowthRatio(float lichen, float moss, float2 q, half detail, float footprint)
{
    float2 c = GP_GrowthCover(lichen, moss, q, detail, footprint);
    half3 r = lerp(1.0h, (half3)_GP_Lichen.rgb, (half)c.x);
    return r * lerp(1.0h, (half3)_GP_Moss.rgb, (half)c.y);
}

// The painted corner's growth over a surface's albedo (the signature its removed surface hook called).
half3 OS_PaintGrowth(half3 albedo, float2 uv0, float lichen, float moss, float sky, float3 positionWS, half3 normalWS,
                     half detail, float footprint)
{
    return albedo * GP_GrowthRatio(lichen, moss, uv0, detail, footprint);
}

#endif
