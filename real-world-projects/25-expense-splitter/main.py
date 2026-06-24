"""
25 - Expense Splitter
Project: Work out who owes whom after a group shares costs.

Record who paid for what and who shared each cost, then it computes everyone's net
balance and the smallest set of payments to settle up. Data is saved to JSON so a trip
or household ledger carries over between runs.

Usage:
  python main.py add --payer Ada --amount 60 --for Ada Grace Linus --desc "Dinner"
  python main.py add --payer Grace --amount 30 --for Ada Grace --desc "Taxi"
  python main.py balances
  python main.py settle
  python main.py reset
"""

import argparse
import json
from pathlib import Path

LEDGER = Path(__file__).parent / "ledger.json"


def load():
    return json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else []


def save(expenses):
    LEDGER.write_text(json.dumps(expenses, indent=2), encoding="utf-8")


def net_balances(expenses):
    """Positive balance = the group owes this person; negative = they owe the group."""
    balances = {}
    for e in expenses:
        share = e["amount"] / len(e["for"])
        balances[e["payer"]] = balances.get(e["payer"], 0) + e["amount"]
        for person in e["for"]:
            balances[person] = balances.get(person, 0) - share
    return {p: round(b, 2) for p, b in balances.items()}


def settle(balances):
    """Greedily match the biggest debtor to the biggest creditor until all are square."""
    debtors = sorted(([p, b] for p, b in balances.items() if b < -0.01), key=lambda x: x[1])
    creditors = sorted(([p, b] for p, b in balances.items() if b > 0.01),
                       key=lambda x: x[1], reverse=True)
    payments = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        owe = -debtors[i][1]
        due = creditors[j][1]
        amount = round(min(owe, due), 2)
        payments.append((debtors[i][0], creditors[j][0], amount))
        debtors[i][1] += amount
        creditors[j][1] -= amount
        if abs(debtors[i][1]) < 0.01:
            i += 1
        if abs(creditors[j][1]) < 0.01:
            j += 1
    return payments


def cmd_add(args):
    expenses = load()
    expenses.append({"payer": args.payer, "amount": args.amount,
                     "for": args.for_, "desc": args.desc or ""})
    save(expenses)
    print(f"Added: {args.payer} paid {args.amount:.2f} for {', '.join(args.for_)}.")


def cmd_balances(args):
    balances = net_balances(load())
    if not balances:
        print("No expenses recorded yet.")
        return
    for person, bal in sorted(balances.items()):
        state = "is owed" if bal > 0 else "owes" if bal < 0 else "is settled"
        print(f"  {person:10} {state} {abs(bal):.2f}")


def cmd_settle(args):
    payments = settle(net_balances(load()))
    if not payments:
        print("Everyone is settled up.")
        return
    print("Settle-up plan:")
    for debtor, creditor, amount in payments:
        print(f"  {debtor} pays {creditor} {amount:.2f}")


def cmd_reset(args):
    if LEDGER.exists():
        LEDGER.unlink()
    print("Ledger cleared.")


def main():
    parser = argparse.ArgumentParser(description="Split shared expenses.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add an expense.")
    p_add.add_argument("--payer", required=True)
    p_add.add_argument("--amount", type=float, required=True)
    p_add.add_argument("--for", dest="for_", nargs="+", required=True,
                       help="People who shared this cost.")
    p_add.add_argument("--desc")
    p_add.set_defaults(func=cmd_add)

    sub.add_parser("balances", help="Show net balances.").set_defaults(func=cmd_balances)
    sub.add_parser("settle", help="Show who pays whom.").set_defaults(func=cmd_settle)
    sub.add_parser("reset", help="Clear the ledger.").set_defaults(func=cmd_reset)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
