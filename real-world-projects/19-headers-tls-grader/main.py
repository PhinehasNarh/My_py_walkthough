"""
19 - HTTP Security Headers + TLS Grader
Project: Grade how well a site is configured for transport and header security.

Fetches a URL, checks for the security response headers that browsers rely on, inspects
the TLS certificate (including days until expiry), and prints a letter grade with the
reasons behind it.

Usage:
  python main.py https://example.com

Authorized use: assess sites you own or are permitted to test.
"""

import argparse
import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

# header -> short reason it matters
SECURITY_HEADERS = {
    "Strict-Transport-Security": "forces HTTPS",
    "Content-Security-Policy": "limits where scripts/resources load from",
    "X-Frame-Options": "blocks clickjacking via framing",
    "X-Content-Type-Options": "stops MIME-type sniffing",
    "Referrer-Policy": "controls referrer leakage",
    "Permissions-Policy": "restricts browser feature access",
}


def check_headers(url: str):
    resp = requests.get(url, timeout=15, headers={"User-Agent": "headers-grader/1.0"})
    present, missing = [], []
    for header, reason in SECURITY_HEADERS.items():
        (present if header in resp.headers else missing).append((header, reason))
    return resp.status_code, present, missing


def check_tls(hostname: str, port: int = 443):
    """Return (cert_subject, days_to_expiry) or None if not HTTPS / on error."""
    ctx = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            proto = ssock.version()
    expires = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    days_left = (expires - datetime.now(timezone.utc)).days
    return proto, days_left


def grade(missing_count: int, tls_ok: bool, days_left) -> str:
    score = 100 - missing_count * 12
    if not tls_ok:
        score -= 40
    if days_left is not None and days_left < 15:
        score -= 15
    for cutoff, letter in [(90, "A"), (80, "B"), (70, "C"), (60, "D")]:
        if score >= cutoff:
            return letter
    return "F"


def main():
    parser = argparse.ArgumentParser(description="Grade a site's security headers and TLS.")
    parser.add_argument("url")
    args = parser.parse_args()

    parsed = urlparse(args.url if "://" in args.url else "https://" + args.url)
    hostname = parsed.hostname
    url = parsed.geturl()

    try:
        status, present, missing = check_headers(url)
    except requests.RequestException as exc:
        print(f"Could not fetch {url}: {exc}")
        return

    print(f"URL: {url}  (HTTP {status})\n")
    print("Present security headers:")
    for h, reason in present:
        print(f"  [x] {h}  ({reason})")
    print("Missing security headers:")
    for h, reason in missing:
        print(f"  [ ] {h}  ({reason})")

    tls_ok, days_left = False, None
    if parsed.scheme == "https":
        try:
            proto, days_left = check_tls(hostname)
            tls_ok = True
            print(f"\nTLS: {proto}, certificate expires in {days_left} day(s).")
        except Exception as exc:
            print(f"\nTLS check failed: {exc}")

    print(f"\nGrade: {grade(len(missing), tls_ok, days_left)}")


if __name__ == "__main__":
    main()
