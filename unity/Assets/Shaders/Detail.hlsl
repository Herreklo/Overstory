#ifndef OVERSTORY_DETAIL_INCLUDED
#define OVERSTORY_DETAIL_INCLUDED

// Detail by distance: true up close, painted from afar (docs/visual-direction.md, Shape). Every layer that draws
// fine marks (growth's crusts, a material's sand and crazing, the grain's relief) asks here how near a pixel is and
// fades its marks into their painted shape and then into a film, so no part needs two versions.

float _OS_NearForce;     // debug: 0 by distance, 1 painted everywhere, 2 the near detail everywhere

// How near a pixel is, for the detail it can carry: true up close, painted from afar (docs/visual-direction.md). 1
// within a couple of metres at eye level (a pixel about a millimetre on the surface), 0 by about seven (four), so
// by the street stop every mark is its painted shape.
half OS_Near(float footprint)
{
#if defined(OS_L5_NEAR)
    return 0.0h;    // (L5's arm, bare-near: every near mark skipped, the painted shape everywhere)
#else
    half n = 1.0h - saturate((half)((footprint - 0.0012) / 0.0028));
    return _OS_NearForce > 1.5 ? 1.0h : (_OS_NearForce > 0.5 ? 0.0h : n);
#endif
}

#endif
