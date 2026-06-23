"""
02 - Subnet & IP Toolkit
Project: Do the IP and subnet maths you constantly need in networking, from one tool.

Pure standard library: Python's ipaddress module does the heavy lifting.

Usage:
  python main.py info 192.168.1.0/24
  python main.py contains 10.0.0.0/8 10.4.5.6
  python main.py split 192.168.1.0/24 4
"""

import argparse
import ipaddress
import math


def describe_network(cidr: str) -> None:
    """Print the key facts about a network given in CIDR form (e.g. 192.168.1.0/24)."""
    # strict=False lets the user pass a host address like 192.168.1.10/24.
    net = ipaddress.ip_network(cidr, strict=False)

    print(f"Network:       {net.with_prefixlen}")
    print(f"Network addr:  {net.network_address}")
    print(f"Broadcast:     {net.broadcast_address}")
    print(f"Netmask:       {net.netmask}")
    print(f"Wildcard:      {net.hostmask}")
    print(f"Total addrs:   {net.num_addresses}")

    hosts = list(net.hosts())
    if hosts:
        print(f"Usable hosts:  {len(hosts)}  ({hosts[0]} - {hosts[-1]})")
    else:
        print("Usable hosts:  0")


def contains(cidr: str, ip: str) -> None:
    net = ipaddress.ip_network(cidr, strict=False)
    addr = ipaddress.ip_address(ip)
    if addr in net:
        print(f"{ip} is INSIDE {net.with_prefixlen}")
    else:
        print(f"{ip} is OUTSIDE {net.with_prefixlen}")


def split_network(cidr: str, count: int) -> None:
    net = ipaddress.ip_network(cidr, strict=False)
    # To get at least `count` subnets we add ceil(log2(count)) bits to the prefix.
    extra_bits = math.ceil(math.log2(count)) if count > 1 else 0
    new_prefix = net.prefixlen + extra_bits
    if new_prefix > net.max_prefixlen:
        print("That network is too small to split that many times.")
        return
    print(f"Splitting {net.with_prefixlen} into {count} subnet(s):")
    for sub in list(net.subnets(new_prefix=new_prefix))[:count]:
        print(f"  {sub.with_prefixlen}")


def main() -> None:
    parser = argparse.ArgumentParser(description="IP and subnet calculator.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_info = sub.add_parser("info", help="Describe a network.")
    p_info.add_argument("cidr", help="Network in CIDR form, e.g. 192.168.1.0/24")

    p_has = sub.add_parser("contains", help="Check if an IP is inside a network.")
    p_has.add_argument("cidr")
    p_has.add_argument("ip")

    p_split = sub.add_parser("split", help="Split a network into N subnets.")
    p_split.add_argument("cidr")
    p_split.add_argument("count", type=int)

    args = parser.parse_args()
    try:
        if args.command == "info":
            describe_network(args.cidr)
        elif args.command == "contains":
            contains(args.cidr, args.ip)
        elif args.command == "split":
            split_network(args.cidr, args.count)
    except ValueError as exc:
        print(f"Invalid input: {exc}")


if __name__ == "__main__":
    main()
