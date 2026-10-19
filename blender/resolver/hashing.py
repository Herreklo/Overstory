"""Deterministic hashing: SplitMix64 over integers and strings.

Every visual choice is seeded from h(worldSeed, buildingId, eventId, purpose, ...).
Never use Python's hash() or random module state: both differ between runs and
languages, and the C# port must produce the same numbers.
"""

M64 = 0xFFFFFFFFFFFFFFFF


def mix(z):
    """SplitMix64 finaliser."""
    z = (z + 0x9E3779B97F4A7C15) & M64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)


def fnv1a(text):
    """64-bit FNV-1a over UTF-8 bytes, for string parts of a key."""
    h = 0xCBF29CE484222325
    for byte in text.encode("utf-8"):
        h ^= byte
        h = (h * 0x100000001B3) & M64
    return h


def h(*parts):
    """Hash a key made of ints and strings into a 64-bit integer."""
    acc = 0x2545F4914F6CDD1D
    for p in parts:
        v = p & M64 if isinstance(p, int) else fnv1a(str(p))
        acc = mix(acc ^ v)
    return acc


def unit(key):
    """A float in [0, 1) from a hash."""
    return (key >> 11) / float(1 << 53)


def between(key, lo, hi):
    """An integer in [lo, hi] from a hash."""
    return lo + key % (hi - lo + 1)


def pick(key, items):
    return items[key % len(items)]


def weighted(key, pairs):
    """pairs: [(item, weight)], integer weights."""
    total = sum(w for _, w in pairs)
    x = key % total
    for item, w in pairs:
        if x < w:
            return item
        x -= w
    return pairs[-1][0]
