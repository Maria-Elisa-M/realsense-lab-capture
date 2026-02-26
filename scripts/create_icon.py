"""Generate a simple assets/icon.ico for the application.

Requires Pillow: pip install pillow
Run from the project root: python scripts/create_icon.py
"""
import struct
import zlib
import sys
import os

OUTPUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "assets", "icon.ico")


def make_png_bytes(size: int) -> bytes:
    """Create a minimal PNG of a solid coloured square (dark + accent dot)."""
    w = h = size
    # Background: #1a1a2e  Accent: #e94560
    bg = (26, 26, 46)
    accent = (233, 69, 96)

    rows = []
    for y in range(h):
        row = bytearray()
        for x in range(w):
            # Simple camera-lens circle in the center
            cx, cy = w / 2, h / 2
            r_outer = w * 0.38
            r_inner = w * 0.18
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if r_inner <= dist <= r_outer:
                row += bytes(accent)
            else:
                row += bytes(bg)
            row += b'\xff'  # alpha
        rows.append(b'\x00' + bytes(row))

    raw = b''.join(rows)
    compressed = zlib.compress(raw, 9)

    def chunk(name: bytes, data: bytes) -> bytes:
        c = name + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)  # 8-bit RGB? No — RGBA
    # Correct: bit_depth=8, colortype=6 (RGBA)
    ihdr_data = struct.pack('>II', w, h) + bytes([8, 6, 0, 0, 0])
    png = sig + chunk(b'IHDR', ihdr_data) + chunk(b'IDAT', compressed) + chunk(b'IEND', b'')
    return png


def make_ico(output_path: str) -> None:
    sizes = [16, 32, 48, 256]
    images = [(s, make_png_bytes(s)) for s in sizes]

    # ICO header
    header = struct.pack('<HHH', 0, 1, len(images))  # reserved, type=1 (ICO), count

    # Directory entries (each 16 bytes)
    offset = 6 + 16 * len(images)
    entries = b''
    for size, data in images:
        w = h = 0 if size == 256 else size  # 0 means 256 in ICO format
        entries += struct.pack('<BBBBHHII', w, h, 0, 0, 1, 32, len(data), offset)
        offset += len(data)

    with open(output_path, 'wb') as f:
        f.write(header + entries)
        for _, data in images:
            f.write(data)

    print(f"Icon created: {output_path}")


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    make_ico(OUTPUT)
