"""
35 - Personal Knowledge Base / Note Search CLI
Project: Make all your scattered notes instantly searchable from the terminal.

Builds a full-text search index over a folder of markdown/text notes using Whoosh, then
lets you search them with ranking and highlighted snippets. Index once, then search as
often as you like; re-indexing picks up new and changed notes.

Usage:
  python main.py index ./notes
  python main.py search "zero trust"
  python main.py search "kerberos" --index ./notes/.kbindex

The index lives in a .kbindex folder next to your notes by default.
"""

import argparse
from pathlib import Path

from whoosh import index
from whoosh.fields import ID, TEXT, Schema
from whoosh.qparser import QueryParser

NOTE_EXTS = {".md", ".txt", ".markdown"}
SCHEMA = Schema(path=ID(stored=True, unique=True),
                title=TEXT(stored=True),
                content=TEXT(stored=True))


def build_index(notes_dir: Path, index_dir: Path) -> int:
    index_dir.mkdir(parents=True, exist_ok=True)
    ix = index.create_in(str(index_dir), SCHEMA)
    writer = ix.writer()
    count = 0
    for path in notes_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in NOTE_EXTS:
            text = path.read_text(encoding="utf-8", errors="ignore")
            writer.add_document(path=str(path), title=path.stem, content=text)
            count += 1
    writer.commit()
    return count


def search(index_dir: Path, query_text: str, limit: int) -> None:
    if not index.exists_in(str(index_dir)):
        print(f"No index at {index_dir}. Run 'index' first.")
        return
    ix = index.open_dir(str(index_dir))
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(query_text)
        results = searcher.search(query, limit=limit)
        results.fragmenter.surround = 40
        print(f"{len(results)} result(s) for '{query_text}':\n")
        for hit in results:
            print(f"  {hit['title']}  ({hit['path']})")
            snippet = hit.highlights("content") or ""
            if snippet:
                print(f"      {snippet.strip()[:160]}")


def default_index_dir(notes_dir: Path) -> Path:
    return notes_dir / ".kbindex"


def main():
    parser = argparse.ArgumentParser(description="Search a folder of notes.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="Build/refresh the search index.")
    p_index.add_argument("notes", type=Path)
    p_index.add_argument("--index", type=Path, help="Where to store the index.")

    p_search = sub.add_parser("search", help="Search the notes.")
    p_search.add_argument("query")
    p_search.add_argument("--index", type=Path, required=True,
                          help="Index folder created by 'index'.")
    p_search.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    if args.command == "index":
        index_dir = args.index or default_index_dir(args.notes)
        n = build_index(args.notes, index_dir)
        print(f"Indexed {n} note(s) into {index_dir}")
    else:
        search(args.index, args.query, args.limit)


if __name__ == "__main__":
    main()
