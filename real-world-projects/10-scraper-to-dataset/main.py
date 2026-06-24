"""
10 - Web Scraper to Dataset
Project: Turn a website's listings into a clean, deduplicated dataset you can analyze.

Defaults to https://quotes.toscrape.com, a site built for scraping practice. It walks
every page, extracts each quote (text, author, tags), removes duplicates, and saves to
CSV. The parsing is split into its own function so you can adapt the selectors to a
different site.

Usage:
  python main.py
  python main.py --out quotes.csv --max-pages 5

Be polite: this only targets sites that allow scraping. Add a delay and respect robots.txt
when pointing it elsewhere.
"""

import argparse
import csv
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

START_URL = "https://quotes.toscrape.com/"
HEADERS = {"User-Agent": "scraper-to-dataset/1.0 (learning project)"}


def parse_page(html: str):
    """Extract the records from one page. Returns (records, next_page_url_or_None)."""
    soup = BeautifulSoup(html, "html.parser")
    records = []
    for quote in soup.select(".quote"):
        records.append({
            "text": quote.select_one(".text").get_text(strip=True),
            "author": quote.select_one(".author").get_text(strip=True),
            "tags": ", ".join(t.get_text(strip=True) for t in quote.select(".tag")),
        })
    next_link = soup.select_one(".next > a")
    next_url = next_link["href"] if next_link else None
    return records, next_url


def scrape(start_url: str, max_pages: int):
    seen = set()
    records = []
    url = start_url
    page = 0
    while url and page < max_pages:
        page += 1
        print(f"Fetching page {page}: {url}")
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        page_records, next_path = parse_page(response.text)

        for rec in page_records:
            if rec["text"] not in seen:        # deduplicate by quote text
                seen.add(rec["text"])
                records.append(rec)

        url = urljoin(url, next_path) if next_path else None
        time.sleep(1)                          # be polite between requests
    return records


def save_csv(records, out_path: str) -> None:
    fields = ["text", "author", "tags"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape a site into a CSV dataset.")
    parser.add_argument("--url", default=START_URL, help="Start URL.")
    parser.add_argument("--out", default="dataset.csv", help="Output CSV file.")
    parser.add_argument("--max-pages", type=int, default=10, help="Page limit.")
    args = parser.parse_args()

    try:
        records = scrape(args.url, args.max_pages)
    except requests.RequestException as exc:
        print(f"Network error: {exc}")
        return

    if not records:
        print("No records found. The site layout may differ from the selectors.")
        return
    save_csv(records, args.out)
    print(f"\nSaved {len(records)} unique record(s) to {args.out}")


if __name__ == "__main__":
    main()
