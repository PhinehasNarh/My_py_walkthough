"""
31 - YARA Malware Triage Scanner
Project: Triage suspicious files by scanning them against pattern-based detection rules.

YARA rules describe byte and string patterns that identify malware families or traits.
This tool compiles a rules file, scans a file or a folder of samples, and reports which
rules matched and where. Writing your own rule is the fastest way to learn how detection
engineering works.

Usage:
  python main.py rules.yar suspicious.exe
  python main.py rules.yar ./samples --recursive

A starter rule (save as rules.yar):
  rule Suspicious_Strings {
      strings: $a = "cmd.exe /c" nocase
               $b = "powershell -enc"
      condition: any of them
  }

Authorized use: triage files you own or are investigating.
"""

import argparse
from pathlib import Path

import yara


def scan_file(rules, path: Path):
    try:
        matches = rules.match(str(path))
    except yara.Error as exc:
        print(f"  {path.name}: could not scan ({exc})")
        return 0
    if not matches:
        return 0
    for m in matches:
        strings = {s.identifier for s in m.strings} if hasattr(m, "strings") else set()
        extra = f"  (strings: {', '.join(sorted(strings))})" if strings else ""
        print(f"  MATCH {path.name}: rule '{m.rule}'{extra}")
    return len(matches)


def main():
    parser = argparse.ArgumentParser(description="Scan files with YARA rules.")
    parser.add_argument("rules", type=Path, help="A .yar rules file.")
    parser.add_argument("target", type=Path, help="A file or folder to scan.")
    parser.add_argument("-r", "--recursive", action="store_true")
    args = parser.parse_args()

    try:
        rules = yara.compile(filepath=str(args.rules))
    except yara.Error as exc:
        print(f"Could not compile rules: {exc}")
        return

    if args.target.is_file():
        files = [args.target]
    elif args.target.is_dir():
        pattern = "**/*" if args.recursive else "*"
        files = [p for p in args.target.glob(pattern) if p.is_file()]
    else:
        print(f"Not found: {args.target}")
        return

    total_matches = 0
    for f in files:
        total_matches += scan_file(rules, f)

    print(f"\nScanned {len(files)} file(s); {total_matches} rule match(es).")


if __name__ == "__main__":
    main()
