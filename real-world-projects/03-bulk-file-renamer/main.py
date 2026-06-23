"""
03 - Bulk File Renamer
Project: Rename a whole folder of files consistently instead of one by one.

Safe by default: it shows a preview (dry run) and only renames when you pass --apply.
It refuses to overwrite existing files and writes an undo file so the last run can be
reversed with --undo.

Usage:
  python main.py ./photos --find "IMG_" --replace "Holiday_"      # preview
  python main.py ./photos --find "IMG_" --replace "Holiday_" --apply
  python main.py ./photos --prefix "2026_" --number --apply
  python main.py ./photos --undo
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

UNDO_FILE = ".rename_undo.json"


def build_new_name(name: str, args, index: int) -> str:
    """Apply the chosen transformations to one filename."""
    new = name
    if args.find is not None:
        new = re.sub(args.find, args.replace, new)
    if args.prefix:
        new = args.prefix + new
    if args.number is not None:
        stem, suffix = Path(new).stem, Path(new).suffix
        new = f"{stem}_{index:03d}{suffix}"
    return new


def plan_renames(folder: Path, args):
    """Work out the (old, new) pairs without touching anything yet."""
    files = sorted(p for p in folder.iterdir() if p.is_file() and p.name != UNDO_FILE)
    if args.ext:
        files = [p for p in files if p.suffix.lower() == args.ext.lower()]

    plan = []
    taken = {p.name for p in folder.iterdir()}
    index = args.number if args.number is not None else 1
    for p in files:
        new_name = build_new_name(p.name, args, index)
        index += 1
        if new_name == p.name:
            continue
        if new_name in taken:
            print(f"SKIP (name clash): {p.name} -> {new_name}")
            continue
        taken.add(new_name)
        plan.append((p.name, new_name))
    return plan


def apply_plan(folder: Path, plan) -> None:
    done = []
    for old, new in plan:
        (folder / old).rename(folder / new)
        done.append((old, new))
    (folder / UNDO_FILE).write_text(
        json.dumps({"time": datetime.now().isoformat(), "renames": done}, indent=2),
        encoding="utf-8",
    )
    print(f"\nRenamed {len(done)} file(s). Undo info saved to {UNDO_FILE}.")


def undo(folder: Path) -> None:
    undo_path = folder / UNDO_FILE
    if not undo_path.exists():
        print("No undo file found in this folder.")
        return
    data = json.loads(undo_path.read_text(encoding="utf-8"))
    restored = 0
    for old, new in reversed(data["renames"]):
        target = folder / new
        if target.exists():
            target.rename(folder / old)
            restored += 1
    undo_path.unlink()
    print(f"Reversed {restored} rename(s).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk rename files in a folder.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--find", help="Regex to search for in each filename.")
    parser.add_argument("--replace", default="", help="Replacement text for --find.")
    parser.add_argument("--prefix", help="Text to add to the front of each name.")
    parser.add_argument("--number", type=int, nargs="?", const=1, default=None,
                        help="Add a sequence number starting at this value (default 1).")
    parser.add_argument("--ext", help="Only rename files with this extension, e.g. .jpg")
    parser.add_argument("--apply", action="store_true", help="Actually perform the renames.")
    parser.add_argument("--undo", action="store_true", help="Reverse the last run in this folder.")
    args = parser.parse_args()

    folder = args.folder
    if not folder.is_dir():
        print(f"Not a folder: {folder}")
        return

    if args.undo:
        undo(folder)
        return

    plan = plan_renames(folder, args)
    if not plan:
        print("Nothing to rename.")
        return

    print("Planned renames:")
    for old, new in plan:
        print(f"  {old}  ->  {new}")

    if args.apply:
        apply_plan(folder, plan)
    else:
        print(f"\nDry run only. Re-run with --apply to rename {len(plan)} file(s).")


if __name__ == "__main__":
    main()
