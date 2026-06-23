"""
04 - File Magic-Byte Type Identifier
Project: Find files whose real type does not match their extension, a classic sign
of something hidden or disguised.

Most file formats start with a known sequence of bytes called a "magic number".
We read the first few bytes of a file, work out its real type, and compare that to
what the extension claims.

Usage:
  python main.py suspicious.jpg
  python main.py ./downloads -r              # scan a folder recursively
  python main.py ./downloads -r --mismatches # only show files that lie about their type
"""

import argparse
from pathlib import Path

# (signature bytes, human-readable type, set of extensions that normally match)
SIGNATURES = [
    (b"\xFF\xD8\xFF", "JPEG image", {".jpg", ".jpeg"}),
    (b"\x89PNG\r\n\x1a\n", "PNG image", {".png"}),
    (b"GIF87a", "GIF image", {".gif"}),
    (b"GIF89a", "GIF image", {".gif"}),
    (b"%PDF", "PDF document", {".pdf"}),
    (b"PK\x03\x04", "ZIP archive (also docx/xlsx/jar/apk)",
     {".zip", ".docx", ".xlsx", ".pptx", ".jar", ".apk"}),
    (b"Rar!\x1a\x07", "RAR archive", {".rar"}),
    (b"\x7fELF", "ELF executable", {".elf", ".so", ""}),
    (b"MZ", "Windows executable", {".exe", ".dll"}),
    (b"\x1f\x8b", "GZIP archive", {".gz"}),
    (b"ID3", "MP3 audio", {".mp3"}),
]


def identify(path: Path):
    """Return (real_type, expected_extensions) or (None, None) if the signature is unknown."""
    try:
        with open(path, "rb") as f:
            head = f.read(16)
    except OSError:
        return None, None
    for sig, name, exts in SIGNATURES:
        if head.startswith(sig):
            return name, exts
    return None, None


def check_file(path: Path, mismatches_only: bool) -> None:
    real_type, exts = identify(path)
    ext = path.suffix.lower()

    if real_type is None:
        if not mismatches_only:
            print(f"?  {path}: unknown signature")
        return

    if ext in exts:
        if not mismatches_only:
            print(f"OK {path}: {real_type}")
    else:
        shown_ext = ext or "(none)"
        print(f"!! {path}: content is {real_type}, but extension is '{shown_ext}'")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect files whose content does not match their extension."
    )
    parser.add_argument("path", type=Path, help="A file or a folder to scan.")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Scan subfolders too.")
    parser.add_argument("--mismatches", action="store_true",
                        help="Only show files whose type does not match the extension.")
    args = parser.parse_args()

    if args.path.is_file():
        files = [args.path]
    elif args.path.is_dir():
        pattern = "**/*" if args.recursive else "*"
        files = sorted(p for p in args.path.glob(pattern) if p.is_file())
    else:
        print(f"Not found: {args.path}")
        return

    for p in files:
        check_file(p, args.mismatches)


if __name__ == "__main__":
    main()
