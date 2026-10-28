#!/usr/bin/env python3
"""The checks a change runs by script before anyone looks at numbers (CLAUDE.md, How work runs). Minimal: only the
walked corner's trees so far.

    python3 tools/check.py

- The corner's trees against their budgets (tools/check_trees.py).

Exits 1 on a failure, 0 when everything built passes.
"""

import argparse
import sys


def main(argv):
    argparse.ArgumentParser().parse_args(argv)
    fails = __import__("check_trees").check()  # the corner's trees (tools/check_trees.py)
    if fails:
        print(f"FAILED: {', '.join(fails)}")
        return 1
    print("passed (what is built)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
