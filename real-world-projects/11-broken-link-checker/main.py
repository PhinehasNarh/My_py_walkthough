"""
11 - Broken Link Checker
Project: Find dead links on a website before your visitors do.

Crawls pages within one site (staying on the same domain), collects every link, and
checks each one's HTTP status. Links that fail or 404 are reported with the page they
were found on. Crawl depth and page count are capped so it stays polite.

Usage:
  python main.py https://example.com
  python main.py https://example.com --max-pages 50 --depth 2
"""

import argparse
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "broken-link-checker/1.0 (learning project)"}


def extract_links(html: str, base_url: str):
    """Return all absolute links found on a page."""
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        links.append(urljoin(base_url, href))
    return links


def same_domain(url: str, root: str) -> bool:
    return urlparse(url).netloc == urlparse(root).netloc


def link_status(url: str) -> int:
    """Return an HTTP status code, or 0 if the request failed entirely."""
    try:
        # HEAD is light; some servers reject it, so fall back to GET.
        resp = requests.head(url, headers=HEADERS, timeout=10, allow_redirects=True)
        if resp.status_code >= 400:
            resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        return resp.status_code
    except requests.RequestException:
        return 0


def crawl(root: str, max_pages: int, max_depth: int):
    queue = deque([(root, 0)])
    visited_pages = set()
    checked = {}     # url -> status, so we never re-check a link
    broken = []      # (status, url, found_on)

    while queue and len(visited_pages) < max_pages:
        page_url, depth = queue.popleft()
        if page_url in visited_pages or depth > max_depth:
            continue
        visited_pages.add(page_url)

        try:
            resp = requests.get(page_url, headers=HEADERS, timeout=10)
        except requests.RequestException as exc:
            print(f"Could not load page {page_url}: {exc}")
            continue

        print(f"[depth {depth}] scanning {page_url}")
        for link in extract_links(resp.text, page_url):
            if link not in checked:
                checked[link] = link_status(link)
                status = checked[link]
                if status == 0 or status >= 400:
                    broken.append((status, link, page_url))
                # Queue internal pages for further crawling.
                if same_domain(link, root) and checked[link] < 400 and checked[link] != 0:
                    queue.append((link, depth + 1))

    return broken, len(checked), len(visited_pages)


def main() -> None:
    parser = argparse.ArgumentParser(description="Find broken links on a site.")
    parser.add_argument("url")
    parser.add_argument("--max-pages", type=int, default=25, help="Most pages to crawl.")
    parser.add_argument("--depth", type=int, default=2, help="How deep to follow links.")
    args = parser.parse_args()

    broken, total_links, pages = crawl(args.url, args.max_pages, args.depth)

    print(f"\nCrawled {pages} page(s), checked {total_links} link(s).")
    if not broken:
        print("No broken links found.")
        return
    print(f"\n{len(broken)} broken link(s):")
    for status, url, found_on in broken:
        label = status if status else "no response"
        print(f"  [{label}] {url}")
        print(f"          found on: {found_on}")


if __name__ == "__main__":
    main()
