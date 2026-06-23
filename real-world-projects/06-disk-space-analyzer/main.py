"""
06 - Disk Space Analyzer
Project: See what is actually eating your disk space instead of guessing.

Walks a folder, totals the size of each immediate child (files and subfolders), and
shows the biggest items first so you know where to look. Pass --csv to save the
breakdown.

Usage:
  python main.py                      # analyze the current folder
  python main.py C:\\Users\\me\\Downloads
  python main.py . -n 20 --csv report.csv
"""

import argparse
import csv
from pathlib import Path


def folder_size(path: Path) -> int:
    """Total size in bytes of everything under a folder."""
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return total


def human(size: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:7.1f} {unit}"
        size /= 1024
    return f"{size:7.1f} PB"


def analyze(root: Path, top: int):
    """Size each immediate child of root and return the largest, biggest first."""
    entries = []
    for child in root.iterdir():
        try:
            size = folder_size(child) if child.is_dir() else child.stat().st_size
        except OSError:
            continue
        entries.append((size, child))
    entries.sort(reverse=True, key=lambda e: e[0])
    return entries[:top] if top else entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Show what is using disk space.")
    parser.add_argument("path", type=Path, nargs="?", default=Path.cwd(),
                        help="Folder to analyze (default: current folder).")
    parser.add_argument("-n", "--top", type=int, default=15, help="Show the top N items.")
    parser.add_argument("--csv", type=Path, help="Save the breakdown to a CSV file.")
    args = parser.parse_args()

    root = args.path
    if not root.is_dir():
        print(f"Not a folder: {root}")
        return

    print(f"Analyzing {root.resolve()} ...\n")
    entries = analyze(root, args.top)
    if not entries:
        print("Folder is empty.")
        return

    total = sum(size for size, _ in entries)
    for size, child in entries:
        kind = "DIR " if child.is_dir() else "file"
        print(f"{human(size)}  {kind}  {child.name}")
    print(f"\nTotal of shown items: {human(total).strip()}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["size_bytes", "type", "name", "path"])
            for size, child in entries:
                writer.writerow([size, "dir" if child.is_dir() else "file",
                                 child.name, str(child)])
        print(f"Saved breakdown to {args.csv}")


if __name__ == "__main__":
    main()
