"""
17 - Secret / API-Key Scanner
Project: Catch API keys and secrets accidentally left in your code.

Walks a folder, matches each line against patterns for well-known secret formats, and
uses a Shannon-entropy check on generic key=value matches to cut down false positives.
Reports the file, line number, and the kind of secret. Pure standard library.

Usage:
  python main.py ./my-project
  python main.py ./my-project --min-entropy 3.5

Authorized use: scan code you own or are permitted to review.
"""

import argparse
import math
import re
from pathlib import Path

# Patterns for clearly-shaped secrets (high confidence).
STRONG_PATTERNS = [
    ("AWS access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Slack token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("GitHub token", re.compile(r"gh[pousr]_[0-9A-Za-z]{36,}")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("JWT", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
]

# Generic "name = value" assignments worth a second look (checked against entropy).
GENERIC_PATTERN = re.compile(
    r"(?i)(api[_-]?key|secret|token|passwd|password|access[_-]?key)\s*[:=]\s*"
    r"['\"]([A-Za-z0-9_\-/+]{12,})['\"]"
)

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "env"}


def shannon_entropy(text: str) -> float:
    """Bits of entropy per character: random-looking strings score higher."""
    if not text:
        return 0.0
    counts = {ch: text.count(ch) for ch in set(text)}
    return -sum((c / len(text)) * math.log2(c / len(text)) for c in counts.values())


def scan_line(line: str, min_entropy: float):
    findings = []
    for label, pattern in STRONG_PATTERNS:
        if pattern.search(line):
            findings.append(label)
    for match in GENERIC_PATTERN.finditer(line):
        value = match.group(2)
        if shannon_entropy(value) >= min_entropy:
            findings.append(f"high-entropy {match.group(1).lower()}")
    return findings


def scan_file(path: Path, min_entropy: float):
    results = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, 1):
                for label in scan_line(line, min_entropy):
                    results.append((lineno, label, line.strip()[:80]))
    except OSError:
        pass
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan a folder for leaked secrets.")
    parser.add_argument("path", type=Path, help="File or folder to scan.")
    parser.add_argument("--min-entropy", type=float, default=3.5,
                        help="Entropy threshold for generic matches (default 3.5).")
    args = parser.parse_args()

    if args.path.is_file():
        files = [args.path]
    else:
        files = [p for p in args.path.rglob("*")
                 if p.is_file() and not SKIP_DIRS & set(p.parts)]

    total = 0
    for f in files:
        for lineno, label, snippet in scan_file(f, args.min_entropy):
            total += 1
            print(f"{f}:{lineno}: [{label}]  {snippet}")

    print(f"\n{total} potential secret(s) found across {len(files)} file(s).")


if __name__ == "__main__":
    main()
