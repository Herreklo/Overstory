"""Wear from use (docs/foundations.md, The shared surface layers, 3; docs/living-fabric.md, uses): every contact of
use wears what it touches. Feet on what is walked on (a hollow, polish, rounded nosings), hands on what is held (a
stair's parapet coping at hand height, a handrail, a door's handle side), boots and bags at a wall's foot beside a
flight, wheels at a corner, sitting on a step or a sill; each polishes, darkens and clears growth where it touches.
How much, from the uses' facts (footfall a year, the years); how deep, from the material (its hardness).

Numpy only; per-vertex arrays in, arrays out.
"""

import numpy as np


def walking(a):
    """Where people walk across a flight or a lane (0 one side, 1 the other): mostly the middle, in two lanes, up and
    down, never the very edges; 1 at the busiest."""
    # (on a flight 3.2 m wide people keep to the middle metre and a half to two; its edges stay quiet)
    p = 0.55 * np.exp(-((a - 0.4) / 0.12) ** 2) + 0.55 * np.exp(-((a - 0.6) / 0.12) ** 2) + 0.15 * np.exp(-((a - 0.5) / 0.22) ** 2)
    return np.clip(p / 0.71, 0.0, 1.0)


def depth(rate, footfall, years, foot):
    """How deep feet have worn it (m): the stone's rate (mm a century at 100,000 footfalls a year) times its use,
    where feet go (foot, 0 to 1)."""
    return rate * (footfall / 1e5) * (years / 100.0) / 1000.0 * foot


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
