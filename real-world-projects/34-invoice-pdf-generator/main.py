"""
34 - Invoice / Receipt PDF Generator
Project: Generate clean, consistent invoices from data instead of editing documents by hand.

Takes client and line-item details (from the command line or a JSON file), computes
subtotals, tax, and total, and renders a tidy PDF invoice with an auto-incrementing
number.

Usage:
  python main.py --client "Acme Ltd" --item "Web design:10:75" --item "Hosting:1:120" --tax 8
  python main.py --from invoice.json

Item format is  description:quantity:unit_price.
"""

import argparse
import json
from datetime import date
from pathlib import Path

from fpdf import FPDF

COUNTER = Path(__file__).parent / ".invoice_no"


def next_invoice_number() -> int:
    n = int(COUNTER.read_text()) + 1 if COUNTER.exists() else 1001
    COUNTER.write_text(str(n))
    return n


def parse_item(text: str) -> dict:
    desc, qty, price = text.rsplit(":", 2)
    return {"desc": desc, "qty": float(qty), "price": float(price)}


def build_pdf(data: dict, out_path: Path) -> None:
    number = data.get("number") or next_invoice_number()
    items = data["items"]
    subtotal = sum(i["qty"] * i["price"] for i in items)
    tax = subtotal * data.get("tax", 0) / 100
    total = subtotal + tax

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "INVOICE")
    pdf.ln(12)
    pdf.set_font("Helvetica", "", 11)
    for line in [f"Invoice #: {number}", f"Date: {date.today().isoformat()}",
                 f"Bill to: {data.get('client', '')}"]:
        pdf.cell(0, 7, line)
        pdf.ln(7)
    pdf.ln(4)

    # Table header. Each cell advances x; pdf.ln ends the row (avoids the deprecated ln= arg).
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(90, 8, "Description", border=1)
    pdf.cell(25, 8, "Qty", border=1, align="R")
    pdf.cell(35, 8, "Unit", border=1, align="R")
    pdf.cell(35, 8, "Amount", border=1, align="R")
    pdf.ln(8)

    pdf.set_font("Helvetica", "", 11)
    for i in items:
        amount = i["qty"] * i["price"]
        pdf.cell(90, 8, i["desc"][:45], border=1)
        pdf.cell(25, 8, f"{i['qty']:g}", border=1, align="R")
        pdf.cell(35, 8, f"{i['price']:.2f}", border=1, align="R")
        pdf.cell(35, 8, f"{amount:.2f}", border=1, align="R")
        pdf.ln(8)

    pdf.ln(2)
    for label, value in [("Subtotal", subtotal), (f"Tax ({data.get('tax', 0):g}%)", tax),
                         ("Total", total)]:
        pdf.set_font("Helvetica", "B" if label == "Total" else "", 11)
        pdf.cell(150, 8, label, align="R")
        pdf.cell(35, 8, f"{value:.2f}", align="R")
        pdf.ln(8)

    pdf.output(str(out_path))
    print(f"Wrote {out_path} (invoice #{number}, total {total:.2f})")


def main():
    parser = argparse.ArgumentParser(description="Generate a PDF invoice.")
    parser.add_argument("--client")
    parser.add_argument("--item", action="append", default=[],
                        help="description:quantity:unit_price (repeatable).")
    parser.add_argument("--tax", type=float, default=0)
    parser.add_argument("--from", dest="from_json", type=Path,
                        help="Read all invoice data from a JSON file.")
    parser.add_argument("--out", type=Path, default=Path("invoice.pdf"))
    args = parser.parse_args()

    if args.from_json:
        data = json.loads(args.from_json.read_text(encoding="utf-8"))
    else:
        if not args.item:
            print("Add at least one --item, or use --from a JSON file.")
            return
        data = {"client": args.client, "tax": args.tax,
                "items": [parse_item(i) for i in args.item]}

    build_pdf(data, args.out)


if __name__ == "__main__":
    main()
