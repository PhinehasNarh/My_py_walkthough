"""
08 - Smart Downloads Organizer
Project: Keep a messy Downloads folder tidy automatically by type and rules.

Sorts the loose files in a folder into category subfolders (Images, Documents, ...).
Moves never overwrite, you can preview with --dry-run, load your own rules from a JSON
file, and keep it running with --watch so new downloads get filed automatically.

Usage:
  python main.py "C:\\Users\\me\\Downloads"
  python main.py "C:\\Users\\me\\Downloads" --dry-run
  python main.py "C:\\Users\\me\\Downloads" --config rules.json
  python main.py "C:\\Users\\me\\Downloads" --watch        # needs: pip install watchdog
"""

import argparse
import json
import shutil
from pathlib import Path

DEFAULT_RULES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt"],
    "Spreadsheets": [".xls", ".xlsx", ".csv", ".ods"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Audio": [".mp3", ".wav", ".flac", ".m4a", ".ogg"],
    "Video": [".mp4", ".mkv", ".mov", ".avi", ".webm"],
    "Installers": [".exe", ".msi", ".dmg", ".pkg"],
    "Code": [".py", ".js", ".html", ".css", ".json", ".ipynb"],
}


def build_lookup(rules: dict) -> dict:
    """Turn {category: [exts]} into {ext: category} for fast lookups."""
    return {ext.lower(): cat for cat, exts in rules.items() for ext in exts}


def unique_destination(dest: Path) -> Path:
    """If dest exists, add _1, _2, ... so we never overwrite a file."""
    if not dest.exists():
        return dest
    stem, suffix, parent = dest.stem, dest.suffix, dest.parent
    i = 1
    while True:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def organize(folder: Path, lookup: dict, dry_run: bool) -> int:
    moved = 0
    category_names = set(lookup.values()) | {"Other"}
    for item in folder.iterdir():
        # Only touch loose files, and never the category folders themselves.
        if not item.is_file() or item.name in category_names:
            continue
        category = lookup.get(item.suffix.lower(), "Other")
        target_dir = folder / category
        dest = unique_destination(target_dir / item.name)

        if dry_run:
            print(f"  would move {item.name}  ->  {category}/{dest.name}")
        else:
            target_dir.mkdir(exist_ok=True)
            shutil.move(str(item), str(dest))
            print(f"  moved {item.name}  ->  {category}/{dest.name}")
        moved += 1
    return moved


def watch(folder: Path, lookup: dict) -> None:
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("Watch mode needs the 'watchdog' package: pip install watchdog")
        return

    class Handler(FileSystemEventHandler):
        def on_created(self, event):
            if not event.is_directory:
                organize(folder, lookup, dry_run=False)

    observer = Observer()
    observer.schedule(Handler(), str(folder), recursive=False)
    observer.start()
    print(f"Watching {folder} ... press Ctrl-C to stop.")
    try:
        while True:
            observer.join(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main() -> None:
    parser = argparse.ArgumentParser(description="Organize a folder by file type.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--config", type=Path, help="JSON file of {category: [extensions]} rules.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without moving anything.")
    parser.add_argument("--watch", action="store_true", help="Keep running and file new arrivals.")
    args = parser.parse_args()

    if not args.folder.is_dir():
        print(f"Not a folder: {args.folder}")
        return

    rules = DEFAULT_RULES
    if args.config:
        rules = json.loads(args.config.read_text(encoding="utf-8"))
    lookup = build_lookup(rules)

    if args.watch:
        watch(args.folder, lookup)
        return

    count = organize(args.folder, lookup, args.dry_run)
    verb = "would be organized" if args.dry_run else "organized"
    print(f"\n{count} file(s) {verb}.")


if __name__ == "__main__":
    main()
