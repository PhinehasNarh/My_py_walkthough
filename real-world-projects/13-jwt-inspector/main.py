"""
13 - JWT Inspector & Weakness Checker
Project: Understand and test JSON Web Tokens used by web apps you are allowed to test.

A JWT is three base64url parts joined by dots: header.payload.signature. This tool
decodes the first two (no key needed), prints the claims in a readable form, checks
for the classic "alg: none" weakness, and can brute-force a weak HS256 secret from a
wordlist. Built on the standard library so you can see exactly how a JWT works.

Usage:
  python main.py <token>
  python main.py <token> --wordlist common-secrets.txt

Authorized use: only test tokens from your own apps or systems you may assess.
"""

import argparse
import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone


def b64url_decode(part: str) -> bytes:
    """Decode a base64url string, adding the padding JWTs leave off."""
    padding = "=" * (-len(part) % 4)
    return base64.urlsafe_b64decode(part + padding)


def split_token(token: str):
    parts = token.strip().split(".")
    if len(parts) != 3:
        raise ValueError("A JWT must have exactly three dot-separated parts.")
    header = json.loads(b64url_decode(parts[0]))
    payload = json.loads(b64url_decode(parts[1]))
    return header, payload, parts


def pretty_claims(payload: dict) -> None:
    print("== Payload claims ==")
    for key, value in payload.items():
        # Turn well-known timestamp claims into readable dates.
        if key in ("exp", "iat", "nbf") and isinstance(value, (int, float)):
            when = datetime.fromtimestamp(value, tz=timezone.utc)
            extra = " (EXPIRED)" if key == "exp" and when < datetime.now(timezone.utc) else ""
            print(f"  {key}: {value}  ->  {when:%Y-%m-%d %H:%M:%S UTC}{extra}")
        else:
            print(f"  {key}: {value}")


def check_none_alg(header: dict) -> None:
    print("\n== Weakness checks ==")
    alg = str(header.get("alg", "")).lower()
    if alg == "none":
        print("  !! alg is 'none': the token is unsigned. A server that accepts this "
              "lets anyone forge tokens.")
    else:
        print(f"  alg is '{header.get('alg')}'. Not the 'none' weakness.")


def brute_hs256(parts, wordlist_path: str) -> None:
    """Try each secret in a wordlist against an HS256 token."""
    signing_input = f"{parts[0]}.{parts[1]}".encode()
    try:
        given_sig = b64url_decode(parts[2])
    except Exception:
        print("  Signature is not valid base64url; cannot brute-force.")
        return

    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            secret = line.strip()
            if not secret:
                continue
            candidate = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
            if hmac.compare_digest(candidate, given_sig):
                print(f"  !! WEAK SECRET FOUND: '{secret}'")
                print("     The token is signed with HS256 using a guessable key.")
                return
    print("  No secret in the wordlist matched (good, or the key is stronger than the list).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect and test a JSON Web Token.")
    parser.add_argument("token", help="The JWT string.")
    parser.add_argument("--wordlist", help="Wordlist to brute-force a weak HS256 secret.")
    args = parser.parse_args()

    try:
        header, payload, parts = split_token(args.token)
    except (ValueError, json.JSONDecodeError, Exception) as exc:
        print(f"Could not parse token: {exc}")
        return

    print("== Header ==")
    for key, value in header.items():
        print(f"  {key}: {value}")
    print()
    pretty_claims(payload)
    check_none_alg(header)

    if args.wordlist and str(header.get("alg", "")).upper() == "HS256":
        print("\n== HS256 secret brute-force ==")
        brute_hs256(parts, args.wordlist)
    elif args.wordlist:
        print("\n  --wordlist only applies to HS256 tokens.")


if __name__ == "__main__":
    main()
