"""
24 - Steganography Tool
Project: Learn how data can be hidden inside images by building hide and extract tools.

Hides a message in the least-significant bits of a PNG's pixels. Each pixel byte gives
up its lowest bit to store one bit of your message, a change too small for the eye to
see. A length header tells the extractor how much to read back.

Usage:
  python main.py hide cover.png "meet at noon" --out secret.png
  python main.py extract secret.png

Authorized use: a learning exercise. Do not use to conceal anything unlawful.
"""

import argparse

from PIL import Image

HEADER_BITS = 32  # first 32 bits store the message length in bytes


def bits_of(data: bytes):
    for byte in data:
        for i in range(7, -1, -1):
            yield (byte >> i) & 1


def hide(cover_path: str, message: str, out_path: str) -> None:
    img = Image.open(cover_path).convert("RGB")
    payload = message.encode("utf-8")
    header = len(payload).to_bytes(4, "big")
    all_bits = list(bits_of(header + payload))

    pixels = list(img.getdata())
    capacity = len(pixels) * 3
    if len(all_bits) > capacity:
        raise ValueError(f"Message too big: needs {len(all_bits)} bits, image holds {capacity}.")

    new_pixels = []
    bit_index = 0
    for r, g, b in pixels:
        channels = [r, g, b]
        for c in range(3):
            if bit_index < len(all_bits):
                channels[c] = (channels[c] & ~1) | all_bits[bit_index]
                bit_index += 1
        new_pixels.append(tuple(channels))

    img.putdata(new_pixels)
    img.save(out_path)
    print(f"Hid {len(payload)} byte(s) in {out_path}")


def extract(stego_path: str) -> None:
    img = Image.open(stego_path).convert("RGB")
    bits = []
    for pixel in img.getdata():
        for channel in pixel:
            bits.append(channel & 1)

    length = int("".join(str(b) for b in bits[:HEADER_BITS]), 2)
    start = HEADER_BITS
    message_bits = bits[start:start + length * 8]

    out = bytearray()
    for i in range(0, len(message_bits), 8):
        byte = 0
        for bit in message_bits[i:i + 8]:
            byte = (byte << 1) | bit
        out.append(byte)
    print("Hidden message:")
    print(out.decode("utf-8", errors="replace"))


def main():
    parser = argparse.ArgumentParser(description="Hide and extract data in PNG images.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_hide = sub.add_parser("hide", help="Hide a message in an image.")
    p_hide.add_argument("cover")
    p_hide.add_argument("message")
    p_hide.add_argument("--out", default="stego.png")

    p_extract = sub.add_parser("extract", help="Extract a hidden message.")
    p_extract.add_argument("image")

    args = parser.parse_args()
    if args.command == "hide":
        hide(args.cover, args.message, args.out)
    else:
        extract(args.image)


if __name__ == "__main__":
    main()
