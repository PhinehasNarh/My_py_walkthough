"""
07 - File Metadata Scrubber
Project: Strip hidden metadata (EXIF, author, GPS) from files before you share them.

Photos and PDFs often carry hidden data: the camera and GPS location of a picture,
the author and software of a document. This tool shows what is embedded and writes a
cleaned copy alongside the original. Originals are never modified.

Usage:
  python main.py photo.jpg                 # report metadata, write photo_clean.jpg
  python main.py report.pdf
  python main.py ./folder --recursive
  python main.py photo.jpg --show-only     # report only, do not write a clean copy

Authorized use: clean your own files before sharing them.
"""

import argparse
from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tiff", ".webp"}
PDF_EXTS = {".pdf"}


def scrub_image(path: Path, show_only: bool) -> None:
    from PIL import Image
    from PIL.ExifTags import TAGS

    with Image.open(path) as img:
        exif = img.getexif()
        if exif:
            print(f"  {len(exif)} EXIF field(s):")
            for tag_id, value in list(exif.items())[:12]:
                name = TAGS.get(tag_id, tag_id)
                print(f"    {name}: {value}")
        else:
            print("  No EXIF metadata found.")

        if show_only:
            return

        # Rebuild the image from raw pixels so no metadata carries over.
        clean = Image.new(img.mode, img.size)
        clean.putdata(list(img.getdata()))
        out = path.with_name(f"{path.stem}_clean{path.suffix}")
        clean.save(out)
        print(f"  Clean copy written: {out.name}")


def scrub_pdf(path: Path, show_only: bool) -> None:
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(str(path))
    meta = reader.metadata or {}
    if meta:
        print("  Document metadata:")
        for key, value in meta.items():
            print(f"    {key}: {value}")
    else:
        print("  No document metadata found.")

    if show_only:
        return

    # Copy the pages into a new document without carrying the metadata over.
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    out = path.with_name(f"{path.stem}_clean{path.suffix}")
    with open(out, "wb") as f:
        writer.write(f)
    print(f"  Clean copy written: {out.name}")


def process(path: Path, show_only: bool) -> None:
    ext = path.suffix.lower()
    print(f"{path.name}:")
    try:
        if ext in IMAGE_EXTS:
            scrub_image(path, show_only)
        elif ext in PDF_EXTS:
            scrub_pdf(path, show_only)
        else:
            print("  Unsupported type, skipped.")
    except Exception as exc:
        print(f"  Error: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Strip metadata from images and PDFs.")
    parser.add_argument("path", type=Path, help="A file or a folder.")
    parser.add_argument("-r", "--recursive", action="store_true", help="Process subfolders too.")
    parser.add_argument("--show-only", action="store_true", help="Report metadata without cleaning.")
    args = parser.parse_args()

    supported = IMAGE_EXTS | PDF_EXTS
    if args.path.is_file():
        files = [args.path]
    elif args.path.is_dir():
        pattern = "**/*" if args.recursive else "*"
        files = [p for p in args.path.glob(pattern)
                 if p.is_file() and p.suffix.lower() in supported
                 and "_clean" not in p.stem]
    else:
        print(f"Not found: {args.path}")
        return

    if not files:
        print("No supported files (images or PDFs) found.")
        return
    for p in files:
        process(p, args.show_only)


if __name__ == "__main__":
    main()
