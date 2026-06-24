"""
26 - Stock / Crypto Portfolio Tracker
Project: Track your holdings' value and get alerted on big moves.

Stores your crypto holdings in a JSON file, fetches live prices from the free CoinGecko
API (no key needed), and reports profit and loss per coin and overall. An optional alert
threshold flags any holding that has moved a lot since you bought it.

Usage:
  python main.py add bitcoin 0.5 30000
  python main.py add ethereum 2 1800
  python main.py show
  python main.py show --alert 10        # flag holdings up/down more than 10%

Prices come from CoinGecko; use the coin's API id (bitcoin, ethereum, solana, ...).
"""

import argparse
import json
from pathlib import Path

import requests

HOLDINGS = Path(__file__).parent / "holdings.json"
PRICE_URL = "https://api.coingecko.com/api/v3/simple/price"


def load():
    return json.loads(HOLDINGS.read_text(encoding="utf-8")) if HOLDINGS.exists() else []


def save(holdings):
    HOLDINGS.write_text(json.dumps(holdings, indent=2), encoding="utf-8")


def fetch_prices(coin_ids, vs="usd"):
    if not coin_ids:
        return {}
    resp = requests.get(PRICE_URL,
                        params={"ids": ",".join(coin_ids), "vs_currencies": vs},
                        timeout=15)
    resp.raise_for_status()
    return {coin: data.get(vs) for coin, data in resp.json().items()}


def compute_rows(holdings, prices):
    """Return per-holding rows with current value and profit/loss percentage."""
    rows = []
    for h in holdings:
        price = prices.get(h["coin"])
        if price is None:
            rows.append({**h, "price": None, "value": None, "pl_pct": None})
            continue
        value = price * h["qty"]
        cost = h["buy_price"] * h["qty"]
        pl_pct = ((value - cost) / cost * 100) if cost else 0.0
        rows.append({**h, "price": price, "value": value, "pl_pct": round(pl_pct, 2)})
    return rows


def cmd_add(args):
    holdings = load()
    holdings.append({"coin": args.coin.lower(), "qty": args.qty, "buy_price": args.buy_price})
    save(holdings)
    print(f"Added {args.qty} {args.coin} at {args.buy_price}.")


def cmd_show(args):
    holdings = load()
    if not holdings:
        print("No holdings yet. Add one with the 'add' command.")
        return
    try:
        prices = fetch_prices([h["coin"] for h in holdings])
    except requests.RequestException as exc:
        print(f"Could not fetch prices: {exc}")
        return

    rows = compute_rows(holdings, prices)
    total_value = total_cost = 0.0
    for r in rows:
        if r["value"] is None:
            print(f"  {r['coin']:12} price unavailable (check the coin id)")
            continue
        total_value += r["value"]
        total_cost += r["buy_price"] * r["qty"]
        alert = ""
        if args.alert and abs(r["pl_pct"]) >= args.alert:
            alert = "  <-- big move"
        print(f"  {r['coin']:12} qty {r['qty']:<8} now ${r['price']:<10,.2f}"
              f" value ${r['value']:<12,.2f} P/L {r['pl_pct']:+.2f}%{alert}")

    if total_cost:
        total_pl = (total_value - total_cost) / total_cost * 100
        print(f"\nPortfolio value: ${total_value:,.2f}  (overall P/L {total_pl:+.2f}%)")


def main():
    parser = argparse.ArgumentParser(description="Track a crypto portfolio.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a holding.")
    p_add.add_argument("coin", help="CoinGecko id, e.g. bitcoin")
    p_add.add_argument("qty", type=float)
    p_add.add_argument("buy_price", type=float)
    p_add.set_defaults(func=cmd_add)

    p_show = sub.add_parser("show", help="Show current value and P/L.")
    p_show.add_argument("--alert", type=float, help="Flag holdings that moved this percent.")
    p_show.set_defaults(func=cmd_show)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
