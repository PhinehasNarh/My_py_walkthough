"""
12 - Email Header Analyzer
Project: Investigate a suspicious email by reading what its headers reveal.

Parses a raw .eml file (or pasted headers), traces the Received hops, reads the
SPF/DKIM/DMARC results, and flags common spoofing signs such as a From address that
disagrees with the Return-Path. Pure standard library.

Usage:
  python main.py suspicious.eml
  python main.py --paste        # paste raw headers, then Ctrl-Z + Enter (Windows) to finish

Authorized use: analyze mail from your own inbox or messages you are allowed to inspect.
"""

import argparse
import re
import sys
from email import message_from_string
from email.utils import parseaddr


def domain_of(address: str) -> str:
    """Pull the domain out of an email address, lowercased."""
    _, addr = parseaddr(address)
    return addr.split("@")[-1].lower() if "@" in addr else ""


def show_addresses(msg) -> None:
    print("== Addresses ==")
    from_dom = domain_of(msg.get("From", ""))
    rp_dom = domain_of(msg.get("Return-Path", ""))
    reply_dom = domain_of(msg.get("Reply-To", ""))

    print(f"  From:        {msg.get('From', '(none)')}")
    print(f"  Return-Path: {msg.get('Return-Path', '(none)')}")
    print(f"  Reply-To:    {msg.get('Reply-To', '(none)')}")

    if from_dom and rp_dom and from_dom != rp_dom:
        print(f"  !! From domain ({from_dom}) does not match Return-Path ({rp_dom}).")
    if reply_dom and from_dom and reply_dom != from_dom:
        print(f"  !! Reply-To domain ({reply_dom}) differs from From ({from_dom}).")


def show_hops(msg) -> None:
    print("\n== Delivery path (oldest first) ==")
    received = msg.get_all("Received", [])
    if not received:
        print("  No Received headers found.")
        return
    # Received headers are listed newest first, so reverse for chronological order.
    for i, hop in enumerate(reversed(received), 1):
        one_line = " ".join(hop.split())
        print(f"  {i}. {one_line[:140]}")


def show_auth(msg) -> None:
    print("\n== Authentication results ==")
    auth = " ".join(msg.get_all("Authentication-Results", []))
    auth += " " + " ".join(msg.get_all("Received-SPF", []))
    if not auth.strip():
        print("  No SPF/DKIM/DMARC results present (the receiver may not have checked).")
        return
    for mech in ("spf", "dkim", "dmarc"):
        match = re.search(rf"{mech}=(\w+)", auth, re.IGNORECASE)
        verdict = match.group(1).lower() if match else "not found"
        flag = "" if verdict in ("pass", "not found") else "  <-- check this"
        print(f"  {mech.upper():5}: {verdict}{flag}")


def analyze(raw: str) -> None:
    msg = message_from_string(raw)
    print(f"Subject: {msg.get('Subject', '(none)')}")
    print(f"Date:    {msg.get('Date', '(none)')}\n")
    show_addresses(msg)
    show_hops(msg)
    show_auth(msg)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze email headers for phishing signs.")
    parser.add_argument("eml", nargs="?", help="Path to a .eml file.")
    parser.add_argument("--paste", action="store_true", help="Paste raw headers via stdin.")
    args = parser.parse_args()

    if args.paste or not args.eml:
        print("Paste the raw email headers, then send EOF (Ctrl-Z + Enter on Windows):")
        raw = sys.stdin.read()
    else:
        raw = open(args.eml, "r", encoding="utf-8", errors="replace").read()

    if not raw.strip():
        print("No input given.")
        return
    analyze(raw)


if __name__ == "__main__":
    main()
