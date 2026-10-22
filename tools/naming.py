"""The naming grammar, read from schemas/naming.md.

The ```regex block in naming.md is the one source of every id and name pattern. Each line is `name: pattern`;
`{other}` stands for another line's pattern, wrapped in a group when it holds a `|` outside brackets.

    from naming import Grammar
    g = Grammar.load()
    g.match("fill", "bld-104/op-f0-0/1")

Run as a script:
    .venv/bin/python tools/naming.py --render   write each schema's patterns from the grammar
    .venv/bin/python tools/naming.py --check    exit 1 if any schema's pattern has drifted from the grammar

A schema marks a pattern as the grammar's with "$comment": "naming: <rule>" beside it; a new one is written as
"pattern": "@@<rule>@@" and filled by --render.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMING = os.path.join(ROOT, "schemas", "naming.md")
SCHEMAS = os.path.join(ROOT, "schemas")

_REF = re.compile(r"\{([a-z0-9-]+)\}")
_PLACEHOLDER = re.compile(r'"pattern": "@@([a-z0-9-]+)@@"')
_RENDERED = re.compile(r'"pattern": ("(?:[^"\\]|\\.)*"), "\$comment": "naming: ([a-z0-9-]+)"')


def _top_alternation(pattern):
    """True when the pattern holds a `|` outside every group and character class."""
    depth, escaped, in_class = 0, False, False
    for c in pattern:
        if escaped:
            escaped = False
        elif c == "\\":
            escaped = True
        elif in_class:
            in_class = c != "]"
        elif c == "[":
            in_class = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "|" and depth == 0:
            return True
    return False


class Grammar(object):
    def __init__(self, raw):
        self.raw = raw
        self._expanded = {}
        self._compiled = {}

    @classmethod
    def load(cls, path=NAMING):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        found = re.search(r"```regex\n(.*?)```", text, re.S)
        if not found:
            raise ValueError("%s has no ```regex block" % path)
        raw = {}
        for n, line in enumerate(found.group(1).splitlines(), 1):
            if not line.strip():
                continue
            name, sep, pattern = line.partition(": ")
            if not sep or not re.match(r"^[a-z0-9-]+$", name):
                raise ValueError("naming.md grammar line %d is not 'name: pattern': %r" % (n, line))
            if name in raw:
                raise ValueError("naming.md names %r twice" % name)
            raw[name] = pattern
        return cls(raw)

    def names(self):
        return list(self.raw)

    def expand(self, name, _stack=()):
        if name not in self.raw:
            raise KeyError("naming.md has no rule %r" % name)
        if name in _stack:
            raise ValueError("naming.md's rule %r refers to itself" % name)
        if name not in self._expanded:
            def sub(m):
                v = self.expand(m.group(1), _stack + (name,))
                return "(?:" + v + ")" if _top_alternation(v) else v
            self._expanded[name] = _REF.sub(sub, self.raw[name])
        return self._expanded[name]

    def anchored(self, name):
        v = self.expand(name)
        return "^(?:" + v + ")$" if _top_alternation(v) else "^" + v + "$"

    def regex(self, name):
        if name not in self._compiled:
            self._compiled[name] = re.compile(self.anchored(name))
        return self._compiled[name]

    def match(self, name, text):
        return isinstance(text, str) and self.regex(name).match(text) is not None


def schema_files():
    return sorted(os.path.join(SCHEMAS, f) for f in os.listdir(SCHEMAS) if f.endswith(".schema.json"))


def render(grammar, text):
    """The schema text with every placeholder and grammar pattern written from the grammar."""
    def placeholder(m):
        name = m.group(1)
        return '"pattern": %s, "$comment": "naming: %s"' % (json.dumps(grammar.anchored(name)), name)

    def rendered(m):
        name = m.group(2)
        return '"pattern": %s, "$comment": "naming: %s"' % (json.dumps(grammar.anchored(name)), name)

    return _RENDERED.sub(rendered, _PLACEHOLDER.sub(placeholder, text))


def drift(grammar):
    """Each (file, rule, problem) where a schema's pattern is not the grammar's."""
    out = []
    for path in schema_files():
        with open(path, encoding="utf-8") as f:
            text = f.read()
        rel = os.path.relpath(path, ROOT)
        for m in _PLACEHOLDER.finditer(text):
            out.append((rel, m.group(1), "unrendered placeholder"))
        for m in _RENDERED.finditer(text):
            name = m.group(2)
            if name not in grammar.raw:
                out.append((rel, name, "no such rule in naming.md"))
            elif json.loads(m.group(1)) != grammar.anchored(name):
                out.append((rel, name, "pattern differs from naming.md"))
    return out


def main(argv):
    grammar = Grammar.load()
    if argv[1:] == ["--render"]:
        for path in schema_files():
            with open(path, encoding="utf-8") as f:
                text = f.read()
            new = render(grammar, text)
            if new != text:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
                print("rendered", os.path.relpath(path, ROOT))
        return 0
    if argv[1:] == ["--check"]:
        problems = drift(grammar)
        for rel, name, why in problems:
            print("%s: %s: %s" % (rel, name, why))
        if not problems:
            print("schema patterns match naming.md (%d rules)" % len(grammar.raw))
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
