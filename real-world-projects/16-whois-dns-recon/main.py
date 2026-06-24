"""
16 - WHOIS & DNS Recon Tool
Project: Gather public registration and DNS information about a domain for recon.

Looks up WHOIS registration details, resolves the common DNS record types, tries a zone
transfer against each nameserver (and reports if one is wrongly allowed), and can
enumerate subdomains from a wordlist.

Usage:
  python main.py example.com
  python main.py example.com --subdomains words.txt

Authorized use: recon on domains you own or are permitted to assess.
"""

import argparse

import dns.resolver
import dns.query
import dns.zone


def whois_lookup(domain: str) -> None:
    print("== WHOIS ==")
    try:
        import whois
        w = whois.whois(domain)
        for label, key in [("Registrar", "registrar"), ("Created", "creation_date"),
                           ("Expires", "expiration_date"), ("Name servers", "name_servers")]:
            print(f"  {label}: {w.get(key)}")
    except Exception as exc:
        print(f"  WHOIS lookup failed: {exc}")


def dns_records(domain: str) -> None:
    print("\n== DNS records ==")
    for rtype in ["A", "AAAA", "MX", "NS", "TXT"]:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            for rdata in answers:
                print(f"  {rtype:5} {rdata.to_text()}")
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            pass
        except Exception:
            pass


def zone_transfer(domain: str) -> None:
    print("\n== Zone transfer (AXFR) test ==")
    try:
        nameservers = [r.to_text() for r in dns.resolver.resolve(domain, "NS")]
    except Exception as exc:
        print(f"  Could not list nameservers: {exc}")
        return
    for ns in nameservers:
        try:
            ns_ip = dns.resolver.resolve(ns, "A")[0].to_text()
            zone = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain, timeout=8))
            names = list(zone.nodes.keys())
            print(f"  !! {ns}: AXFR ALLOWED (leaked {len(names)} records). This is a misconfiguration.")
        except Exception:
            print(f"  {ns}: refused (good).")


def subdomain_enum(domain: str, wordlist: str) -> None:
    print("\n== Subdomain enumeration ==")
    with open(wordlist, "r", encoding="utf-8", errors="ignore") as f:
        words = [w.strip() for w in f if w.strip()]
    found = 0
    for word in words:
        host = f"{word}.{domain}"
        try:
            answers = dns.resolver.resolve(host, "A")
            print(f"  {host} -> {answers[0].to_text()}")
            found += 1
        except Exception:
            pass
    print(f"  {found} subdomain(s) resolved out of {len(words)} tried.")


def main():
    parser = argparse.ArgumentParser(description="WHOIS and DNS recon for a domain.")
    parser.add_argument("domain")
    parser.add_argument("--subdomains", help="Wordlist file for subdomain enumeration.")
    parser.add_argument("--no-whois", action="store_true", help="Skip the WHOIS lookup.")
    args = parser.parse_args()

    if not args.no_whois:
        whois_lookup(args.domain)
    dns_records(args.domain)
    zone_transfer(args.domain)
    if args.subdomains:
        subdomain_enum(args.domain, args.subdomains)


if __name__ == "__main__":
    main()
