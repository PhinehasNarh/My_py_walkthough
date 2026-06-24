"""
33 - Wordlist / Breach Corpus Analyzer
Project: Understand how people actually pick passwords by analyzing a public breach wordlist.

Streams a large password list (so it never loads the whole file into memory) and reports
length distribution, character-class makeup, the most common passwords, and common
structural patterns. Optionally saves a length-distribution chart.

Usage:
  python main.py rockyou.txt
  python main.py rockyou.txt --top 20 --chart lengths.png

Authorized use: analyze public wordlists for learning and defensive policy work.
"""

import argparse
from collections import Counter
from pathlib import Path


def classify(pw: str) -> str:
    """Describe the character makeup of one password."""
    has_lower = any(c.islower() for c in pw)
    has_upper = any(c.isupper() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    has_symbol = any(not c.isalnum() for c in pw)
    if has_lower and not (has_upper or has_digit or has_symbol):
        return "all lowercase"
    if has_digit and not (has_lower or has_upper or has_symbol):
        return "all digits"
    if pw[:-1].isalpha() and pw[-1:].isdigit():
        return "letters + trailing digit"
    if has_lower and has_digit and not (has_upper or has_symbol):
        return "lowercase + digits"
    return "mixed / complex"


def analyze(path: Path):
    lengths = Counter()
    patterns = Counter()
    common = Counter()
    total = 0
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            pw = line.rstrip("\n")
            if not pw:
                continue
            total += 1
            lengths[len(pw)] += 1
            patterns[classify(pw)] += 1
            common[pw] += 1
    return total, lengths, patterns, common


def maybe_chart(lengths, out_path):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("(install matplotlib to enable charts: pip install matplotlib)")
        return
    xs = sorted(lengths)
    plt.bar(xs, [lengths[x] for x in xs])
    plt.xlabel("password length")
    plt.ylabel("count")
    plt.title("Password length distribution")
    plt.savefig(out_path)
    print(f"Chart saved to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze a password wordlist.")
    parser.add_argument("wordlist", type=Path)
    parser.add_argument("--top", type=int, default=15, help="How many top passwords to show.")
    parser.add_argument("--chart", help="Save a length-distribution chart to this PNG.")
    args = parser.parse_args()

    if not args.wordlist.is_file():
        print(f"Not a file: {args.wordlist}")
        return

    total, lengths, patterns, common = analyze(args.wordlist)
    if not total:
        print("Wordlist is empty.")
        return

    print(f"Analyzed {total:,} password(s).\n")

    print("Length distribution (most common first):")
    for length, n in lengths.most_common(8):
        print(f"  {length:2} chars: {n:>10,}  ({100 * n / total:.1f}%)")

    print("\nStructural patterns:")
    for pattern, n in patterns.most_common():
        print(f"  {pattern:24} {n:>10,}  ({100 * n / total:.1f}%)")

    print(f"\nTop {args.top} passwords:")
    for pw, n in common.most_common(args.top):
        print(f"  {n:>8,}  {pw}")

    if args.chart:
        maybe_chart(lengths, args.chart)


if __name__ == "__main__":
    main()
