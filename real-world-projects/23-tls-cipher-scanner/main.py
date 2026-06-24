"""
23 - TLS / Cipher Suite Scanner
Project: See which TLS versions and ciphers a server accepts, on hosts you are allowed to test.

Probes each TLS protocol version a server will negotiate, reports the cipher it agrees on,
and flags anything outdated (TLS 1.0 / 1.1 or a weak cipher). Pure standard library
(your local OpenSSL decides which versions can even be attempted).

Usage:
  python main.py github.com
  python main.py example.com 443

Authorized use: only scan hosts you own or are permitted to test.
"""

import argparse
import socket
import ssl

# Protocol versions we will try to force, newest to oldest.
PROTOCOLS = [
    ("TLS 1.3", ssl.TLSVersion.TLSv1_3),
    ("TLS 1.2", ssl.TLSVersion.TLSv1_2),
    ("TLS 1.1", ssl.TLSVersion.TLSv1_1),
    ("TLS 1.0", ssl.TLSVersion.TLSv1),
]

WEAK_VERSIONS = {"TLS 1.0", "TLS 1.1"}
WEAK_CIPHER_HINTS = ("RC4", "3DES", "DES", "MD5", "NULL", "EXPORT")


def try_version(host: str, port: int, version) -> tuple:
    """Force a single TLS version. Returns (negotiated_proto, cipher) or (None, None)."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        ctx.minimum_version = version
        ctx.maximum_version = version
    except ValueError:
        return None, None  # this Python/OpenSSL cannot offer that version
    try:
        with socket.create_connection((host, port), timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cipher_name = ssock.cipher()[0]
                return ssock.version(), cipher_name
    except ( ssl.SSLError, socket.error, OSError):
        return None, None


def main():
    parser = argparse.ArgumentParser(description="Scan a server's TLS versions and ciphers.")
    parser.add_argument("host")
    parser.add_argument("port", type=int, nargs="?", default=443)
    args = parser.parse_args()

    print(f"Scanning {args.host}:{args.port}\n")
    accepted = []
    for label, version in PROTOCOLS:
        proto, cipher = try_version(args.host, args.port, version)
        if proto:
            accepted.append((label, cipher))
            weak = " <-- outdated" if label in WEAK_VERSIONS else ""
            cipher_weak = " <-- weak cipher" if any(h in cipher for h in WEAK_CIPHER_HINTS) else ""
            print(f"  accepted  {label:8} cipher: {cipher}{weak}{cipher_weak}")
        else:
            print(f"  rejected  {label}")

    if not accepted:
        print("\nNo TLS connection negotiated (host unreachable or non-TLS port).")
        return
    if any(label in WEAK_VERSIONS for label, _ in accepted):
        print("\nResult: server still allows outdated TLS. Disable TLS 1.0/1.1.")
    else:
        print("\nResult: only modern TLS accepted. Good.")


if __name__ == "__main__":
    main()
