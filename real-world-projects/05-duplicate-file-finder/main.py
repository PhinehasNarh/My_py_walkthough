"""
05 - Duplicate File Finder
Project: Reclaim disk space by finding exact duplicate files across folders.

The trick for speed: two files can only be identical if they are the same size, so
we group by size first (cheap) and only hash files that share a size. Identical
content produces an identical hash, so matching hashes mean duplicate files.

Usage:
  python main.py ./downloads
  python main.py ./downloads ./desktop          # scan several folders at once
  python main.py ./downloads --delete           # remove extras (keeps one of each)
"""

import argparse
import hashlib
from collections import defaultdict
from pathlib import Path


def file_hash(path: Path, chunk_size: int = 65536) -> str:
    """SHA-256 of a file, read in chunks so big files do not fill memory."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(folders):
    # Step 1: group every file by size.
    by_size = defaultdict(list)
    for folder in folders:
        for p in folder.rglob("*"):
            if p.is_file():
                try:
                    by_size[p.stat().st_size].append(p)
                except OSError:
                    pass

    # Step 2: only hash files that share a size with another file.
    by_hash = defaultdict(list)
    for paths in by_size.values():
        if len(paths) < 2:
            continue
        for p in paths:
            try:
                by_hash[file_hash(p)].append(p)
            except OSError:
                pass

    # Keep only the groups that really are duplicates.
    return {h: paths for h, paths in by_hash.items() if len(paths) > 1}


def human(size: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def main() -> None:
    parser = argparse.ArgumentParser(description="Find duplicate files by content.")
    parser.add_argument("folders", nargs="+", type=Path, help="One or more folders to scan.")
    parser.add_argument("--delete", action="store_true",
                        help="Delete the extra copies (keeps the first of each set).")
    args = parser.parse_args()

    folders = [f for f in args.folders if f.is_dir()]
    if not folders:
        print("No valid folders given.")
        return

    dupes = find_duplicates(folders)
    if not dupes:
        print("No duplicates found.")
        return

    wasted = 0
    for paths in dupes.values():
        size = paths[0].stat().st_size
        wasted += size * (len(paths) - 1)
        print(f"\nDuplicate set ({human(size)} each):")
        for i, p in enumerate(paths):
            tag = "keep " if i == 0 else "extra"
            print(f"  [{tag}] {p}")

    print(f"\nWasted space: {human(wasted)} across {len(dupes)} set(s).")

    if args.delete:
        confirm = input("\nDelete all extra copies? Type 'yes' to confirm: ")
        if confirm.strip().lower() != "yes":
            print("Nothing deleted.")
            return
        removed = 0
        for paths in dupes.values():
            for p in paths[1:]:
                try:
                    p.unlink()
                    removed += 1
                except OSError as exc:
                    print(f"Could not delete {p}: {exc}")
        print(f"Deleted {removed} file(s).")


if __name__ == "__main__":
    main()
