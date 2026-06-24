"""
15 - Screenshot OCR Tool
Project: Pull text out of screenshots and images instead of retyping it.

Runs optical character recognition on an image and prints the text, optionally copying
it to the clipboard or saving it to a file. You can also OCR a whole folder of images.

Requirements:
  pip install -r requirements.txt
  Plus the Tesseract OCR engine itself (pytesseract is just a wrapper):
    Windows: https://github.com/UB-Mannheim/tesseract/wiki
    macOS:   brew install tesseract
    Linux:   sudo apt install tesseract-ocr

Usage:
  python main.py screenshot.png
  python main.py screenshot.png --copy
  python main.py ./images --out extracted.txt
"""

import argparse
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".webp"}


def ocr_image(path: Path) -> str:
    from PIL import Image
    import pytesseract

    with Image.open(path) as img:
        text = pytesseract.image_to_string(img)
    # Collapse the blank lines OCR tends to produce.
    return "\n".join(line for line in text.splitlines() if line.strip())


def copy_to_clipboard(text: str) -> bool:
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def gather(path: Path):
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(p for p in path.glob("*") if p.suffix.lower() in IMAGE_EXTS)
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from images with OCR.")
    parser.add_argument("path", type=Path, help="An image file or a folder of images.")
    parser.add_argument("--copy", action="store_true", help="Copy the result to the clipboard.")
    parser.add_argument("--out", type=Path, help="Save the extracted text to this file.")
    args = parser.parse_args()

    images = gather(args.path)
    if not images:
        print(f"No image found at {args.path}")
        return

    try:
        import pytesseract  # noqa: F401  (checked here to give a clear error early)
    except ImportError:
        print("Missing dependency. Run: pip install -r requirements.txt")
        return

    all_text = []
    for img in images:
        print(f"--- {img.name} ---")
        try:
            text = ocr_image(img)
        except Exception as exc:
            # The most common cause is Tesseract not being installed or not on PATH.
            print(f"  OCR failed: {exc}")
            print("  Make sure the Tesseract engine is installed (see the file header).")
            continue
        print(text or "  (no text detected)")
        all_text.append(f"# {img.name}\n{text}")

    combined = "\n\n".join(all_text)
    if combined and args.out:
        args.out.write_text(combined, encoding="utf-8")
        print(f"\nSaved text to {args.out}")
    if combined and args.copy:
        ok = copy_to_clipboard(combined)
        print("Copied to clipboard." if ok else "Clipboard copy needs: pip install pyperclip")


if __name__ == "__main__":
    main()
