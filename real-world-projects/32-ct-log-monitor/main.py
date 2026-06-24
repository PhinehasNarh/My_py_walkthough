"""
32 - Certificate Transparency Monitor
Project: Detect rogue or unexpected certificates issued for your domain.

Every publicly trusted certificate is logged in Certificate Transparency logs. This tool
queries crt.sh for all certificates issued for a domain (and its subdomains), compares
them against a saved baseline, and flags anything new, which can be an early sign of
phishing or a misissued certificate.

Usage:
  python main.py example.com                       # first run saves a baseline
  python main.py example.com --baseline example.json   # later runs flag new certs

Authorized use: monitor domains you own.
"""

import argparse
import json
from pathlib import Path

import requests

CRT_SH = "https://crt.sh/"


def fetch_certs(domain: str):
    """Return a set of (issuer, common_name) seen in CT logs for the domain."""
    resp = requests.get(CRT_SH, params={"q": f"%.{domain}", "output": "json"},
                        timeout=30, headers={"User-Agent": "ct-monitor/1.0"})
    resp.raise_for_status()
    seen = set()
    for entry in resp.json():
        issuer = entry.get("issuer_name", "").strip()
        for name in entry.get("name_value", "").splitlines():
            seen.add((issuer, name.strip()))
    return seen


def load_baseline(path: Path):
    if path and path.exists():
        return {tuple(item) for item in json.loads(path.read_text(encoding="utf-8"))}
    return set()


def save_baseline(path: Path, certs):
    path.write_text(json.dumps(sorted(certs)), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Watch CT logs for new certificates.")
    parser.add_argument("domain")
    parser.add_argument("--baseline", type=Path,
                        help="Baseline file to compare against and update.")
    args = parser.parse_args()

    try:
        current = fetch_certs(args.domain)
    except requests.RequestException as exc:
        print(f"Could not query crt.sh: {exc}")
        return
    except ValueError:
        print("crt.sh returned no parseable data (it can be flaky; try again).")
        return

    print(f"Found {len(current)} certificate name(s) for {args.domain} in CT logs.")

    baseline_path = args.baseline or Path(f"{args.domain}-ct-baseline.json")
    baseline = load_baseline(baseline_path)

    if not baseline:
        save_baseline(baseline_path, current)
        print(f"Baseline saved to {baseline_path}. Re-run later to detect new certificates.")
        return

    new_certs = current - baseline
    if not new_certs:
        print("No new certificates since the last baseline.")
    else:
        print(f"\n{len(new_certs)} NEW certificate(s) detected:")
        for issuer, name in sorted(new_certs):
            print(f"  {name}")
            print(f"      issued by: {issuer}")
    save_baseline(baseline_path, current)


if __name__ == "__main__":
    main()
