#!/usr/bin/env python3
"""List string literals in JS files that look like user-facing English text.

Usage: python3 tools/extract_strings.py main.js [more.js ...]
Prints "file:line: literal" for each candidate. Used to audit translation coverage.
"""
import re
import sys

# Matches single- or double-quoted JS string literals (no template literals in this codebase).
STR_RE = re.compile(r'"((?:[^"\\\n]|\\.)*)"|\'((?:[^\'\\\n]|\\.)*)\'')

# Literals that are clearly code (element ids, css values, storage keys) are skipped.
SKIP_RE = re.compile(
    r'^(?:[a-zA-Z0-9_\-]+|#?[0-9a-fA-F]{3,8}|\d+px|[\d.]+|rgba?\(.*\)|block|none|inline|visible|hidden)$'
)


def candidates(path):
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            for m in STR_RE.finditer(line):
                lit = m.group(1) if m.group(1) is not None else m.group(2)
                if not re.search(r"[A-Za-z]", lit):
                    continue
                before = line[: m.start()].rstrip()
                # Element ids and storage keys are code, not text.
                if re.search(r"(getElementById|getItem|setItem|removeItem|addEventListener|createElement|setAttribute)\($", before):
                    continue
                # Lowercase/camelCase identifiers and css values are code; keep capitalized single words.
                if SKIP_RE.match(lit) and not re.match(r"^[A-Z]", lit):
                    continue
                yield lineno, lit


def main():
    for path in sys.argv[1:]:
        for lineno, lit in candidates(path):
            print(f"{path}:{lineno}: {lit}")


if __name__ == "__main__":
    main()
