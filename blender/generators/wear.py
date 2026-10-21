"""Wear from use (docs/foundations.md, The shared surface layers, 3; docs/living-fabric.md, uses): every contact of
use wears what it touches. Feet on what is walked on (a hollow, polish, rounded nosings), hands on what is held (a
stair's parapet coping at hand height, a handrail, a door's handle side), boots and bags at a wall's foot beside a
flight, wheels at a corner, sitting on a step or a sill; each polishes, darkens and clears growth where it touches.
How much, from the uses' facts (footfall a year, the years); how deep, from the material (its hardness).

Numpy only; per-vertex arrays in, arrays out.
"""

import numpy as np


def walking(a, width=3.2, lean=0.0):
    """Where people walk across a flight or a lane (a: 0 one side, 1 the other), 1 at the busiest; in metres, so a
    narrow passage is walked single file down its middle and a wide flight in two lanes, one each way, never at the
    very edges. lean (-1 to 1): the side the line keeps to (a rail or a wall to hold, the door it leads to, the inside
    of a bend), from the flight's facts (one symmetric line on every flight read as a copy)."""
    x = (np.asarray(a, float) - 0.5) * width - lean * min(0.25 * width, 0.5)
    if width < 1.8:
        p = np.exp(-(x / max(0.2 * width, 0.22)) ** 2)
    else:
        p = 0.55 * np.exp(-((x + 0.32) / 0.38) ** 2) + 0.55 * np.exp(-((x - 0.32) / 0.38) ** 2) + \
            0.15 * np.exp(-(x / 0.7) ** 2)
        p = p / 0.71
    return np.clip(p, 0.0, 1.0)


def depth(rate, footfall, years, foot, width=3.2):
    """How deep feet have worn it (m): the stone's rate (mm a century at 100,000 footfalls a year on a flight 3.2 m
    wide) times its use, where feet go (foot, 0 to 1); a narrow flight takes the same feet on fewer foot-widths."""
    return rate * (footfall / 1e5) * float(np.clip(3.2 / max(width, 0.8), 0.6, 2.5)) * (years / 100.0) / 1000.0 * foot


def polish(footfall, years, foot):
    """How polished feet have left it (0 to 1): it comes within a few years of use and keeps."""
    return np.clip(1.0 - np.exp(-footfall * min(years, 40) / 4e5), 0.0, 1.0) * foot


def nosing(worn, busy):
    """How much a nosing's arris rounds beyond the tread's hollow: it takes the heel and toe of every step and rounds
    several times faster (docs/research/stone.md: nosings rounded)."""
    return worn * 4.0 * busy


def hands(height, use, reach=0.95, band=0.35):
    """Hands on what stands at hand height beside a flight (a parapet's coping, a rail): height above the step (m),
    use (0 to 1: how steep and busy the flight)."""
    return float(np.clip(1.0 - abs(height - reach) / band, 0.0, 1.0)) * use


def boots(above, use):
    """Boots, bags and barrows at a wall's foot beside a flight: above (m over the step beside it)."""
    return np.clip(1.0 - np.abs(above - 0.06) / 0.14, 0.0, 1.0) * 0.5 * use


def busy(footfall, width):
    """How hard the walking line is trodden (0 to 1), from the footfall and the width it spreads over: growth dies
    fast under feet (no plot kept half its cover after 200 passes; docs/research/stone.md), so a busy flight's line
    is bare and a doorstep used a few times a day keeps lichen and moss almost everywhere (the walking line's shape
    alone made every flight grow alike)."""
    passes = footfall / max(width / 0.4, 1.0)      # a year, on one foot-width of the line
    return float(1.0 - np.exp(-passes / 1500.0))
