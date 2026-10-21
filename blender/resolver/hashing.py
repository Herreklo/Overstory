"""Deterministic hashing: the project's one hash spec (docs/building-blocks.md, Seeds and determinism).

Every visual choice is seeded from h(worldSeed, id, purpose, ...): a stable id (a record, slot, fill or part path)
and what the number is for. Never Python's hash() (salted per process), the random module (its streams may change
between Python versions), numpy's Generator, or a key made from a formatted float (it re-draws a neighbour when a
piece moves). The C# twin, unity/Assets/Code/Core/Hash.cs, matches this exactly; both reproduce
fixtures/golden/hash-vectors.json (blender/resolver/hash_vectors.py writes and checks it).

The spec:
- fnv1a(text): 64-bit FNV-1a over the text's UTF-8 bytes (offset 0xCBF29CE484222325, prime 0x100000001B3).
- mix(z): SplitMix64's step and finaliser: z + 0x9E3779B97F4A7C15, then the two xor-shift-multiplies.
- h(*parts): start at 0x2545F4914F6CDD1D; for each part, an int as its 64-bit two's complement, a string as its
  fnv1a; acc = mix(acc ^ part). h() of nothing is the start.
- unit(key) = (key >> 11) / 2^53, in [0, 1); between, pick and weighted take the key modulo their range.
- Stream(*key): a SplitMix64 sequence whose state starts at h(*key); draw n is mix(h(*key) + n * 0x9E3779B97F4A7C15).
  For the many draws one judged part function makes from its own seed, in a fixed order. A choice that must not
  move when other draws are added or dropped takes its own key, h(id, purpose), instead of a place in a stream.

Key parts are ints and strings only: an id formatted with integers is stable, a float never is.
"""

M64 = 0xFFFFFFFFFFFFFFFF
START = 0x2545F4914F6CDD1D
GAMMA = 0x9E3779B97F4A7C15


def mix(z):
    """SplitMix64: one step (+ GAMMA) and its finaliser."""
    z = (z + GAMMA) & M64
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
    acc = START
    for p in parts:
        v = p & M64 if isinstance(p, int) else fnv1a(str(p))
        acc = mix(acc ^ v)
    return acc


def unit(key):
    """A float in [0, 1) from a hash."""
    return (key >> 11) / float(1 << 53)


def uniform(key, lo, hi):
    """A float in [lo, hi) from a hash (lo + (hi - lo) * unit)."""
    return lo + (hi - lo) * unit(key)


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


class Stream:
    """A SplitMix64 sequence seeded from a key (see the spec above). Its methods are named as the random module's, so
    a part function's draws read as before; each takes the next 64 bits."""

    __slots__ = ("state",)

    def __init__(self, *key):
        self.state = h(*key)

    def next(self):
        """The next 64-bit draw."""
        v = mix(self.state)
        self.state = (self.state + GAMMA) & M64
        return v

    def random(self):
        """A float in [0, 1)."""
        return unit(self.next())

    def uniform(self, a, b):
        """A float between a and b (a + (b - a) * random(), as the random module)."""
        return a + (b - a) * self.random()

    def randint(self, a, b):
        """An integer in [a, b]."""
        return between(self.next(), a, b)

    def randrange(self, a, b=None):
        """An integer in [a, b), or [0, a) with one argument."""
        lo, hi = (0, a) if b is None else (a, b)
        return between(self.next(), lo, hi - 1)

    def choice(self, items):
        return pick(self.next(), items)

    def weighted(self, pairs):
        """One item of [(item, weight)] by integer weight."""
        return weighted(self.next(), pairs)

    def normal(self, mu=0.0, sigma=1.0):
        """A normal draw by Irwin and Hall: twelve units less six (mean 0, spread 1, within six spreads). Only sums,
        so it is the same in every language."""
        s = 0.0
        for _ in range(12):
            s += self.random()
        return mu + sigma * (s - 6.0)
