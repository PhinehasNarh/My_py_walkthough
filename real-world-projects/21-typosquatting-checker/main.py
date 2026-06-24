"""
21 - Typosquatting Domain Checker
Project: Find lookalike domains that could be used to impersonate a brand.

Generates common typo variants of a domain (character swaps, omissions, repeats,
adjacent-key slips, and a few homoglyphs), checks which ones actually resolve in DNS,
and reports the live lookalikes so you can watch for impersonation.

Usage:
  python main.py mybrand.com
  python main.py mybrand.com --tlds com net org io co

Authorized use: monitor domains and brands you own.
"""

import argparse

import dns.resolver

# Keys next to each other on a QWERTY keyboard, for realistic "fat finger" typos.
ADJACENT = {
    "a": "qsz", "b": "vghn", "c": "xdfv", "d": "serfcx", "e": "wsdr",
    "f": "drtgvc", "g": "ftyhbv", "h": "gyujnb", "i": "ujko", "j": "huikmn",
    "k": "jiolm", "l": "kop", "m": "njk", "n": "bhjm", "o": "iklp",
    "p": "ol", "q": "wa", "r": "edft", "s": "awedxz", "t": "rfgy",
    "u": "yhji", "v": "cfgb", "w": "qase", "x": "zsdc", "y": "tghu", "z": "asx",
}
HOMOGLYPHS = {"o": "0", "l": "1", "i": "1", "e": "3", "a": "4", "s": "5"}


def variants(name: str):
    """Generate typo variants of the domain name (without its TLD)."""
    out = set()
    for i in range(len(name)):
        out.add(name[:i] + name[i + 1:])                       # omission
        out.add(name[:i] + name[i] + name[i] + name[i + 1:])   # repeated char
        if i < len(name) - 1:                                  # swap neighbours
            out.add(name[:i] + name[i + 1] + name[i] + name[i + 2:])
        for adj in ADJACENT.get(name[i], ""):                  # adjacent-key slip
            out.add(name[:i] + adj + name[i + 1:])
        if name[i] in HOMOGLYPHS:                              # lookalike character
            out.add(name[:i] + HOMOGLYPHS[name[i]] + name[i + 1:])
    out.discard(name)
    return sorted(out)


def resolves(domain: str):
    """Return the resolved IP as text, or None if the domain does not resolve."""
    try:
        return dns.resolver.resolve(domain, "A")[0].to_text()
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Find live lookalike domains.")
    parser.add_argument("domain", help="The real domain, e.g. mybrand.com")
    parser.add_argument("--tlds", nargs="+", default=None,
                        help="Also try these TLDs on the typo variants.")
    args = parser.parse_args()

    if "." not in args.domain:
        print("Please give a full domain like mybrand.com")
        return
    name, _, tld = args.domain.partition(".")
    tlds = args.tlds or [tld]

    candidates = []
    for variant in variants(name):
        for t in tlds:
            candidates.append(f"{variant}.{t}")
    # Also try the exact name on other TLDs (a common impersonation trick).
    for t in tlds:
        if t != tld:
            candidates.append(f"{name}.{t}")

    print(f"Checking {len(candidates)} lookalike(s) of {args.domain} ...\n")
    live = 0
    for candidate in sorted(set(candidates)):
        ip = resolves(candidate)
        if ip:
            live += 1
            print(f"  LIVE  {candidate:30} -> {ip}")
    print(f"\n{live} lookalike domain(s) resolve and may need watching.")


if __name__ == "__main__":
    main()
