#!/usr/bin/env python3
"""Convert avatar.png or source-prepped.png into a self-typing monochrome ASCII SVG.

Each row wipes in left-to-right with a block cursor riding the edge,
staggered top to bottom. SMIL only - GitHub plays it inside <img>.

Usage: python scripts/make_ascii_svg.py [--input avatar.png] [--cols 75]
Writes ascii-portrait.svg.
"""
import html
import os
import sys
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = blank bg
COLS = 75
CHAR_W = 7.2  # px per glyph at font-size 12 monospace
CHAR_H = 12.6
FG = "#c9d1d9"
BG = "#0d1117"
ROW_WIPE = 0.55  # seconds each row takes to print
ROW_STAGGER = 0.06  # delay between row starts


def main() -> None:
    cols = COLS
    src_file = "source-prepped.png" if os.path.exists("source-prepped.png") else "avatar.png"

    if "--cols" in sys.argv:
        cols = int(sys.argv[sys.argv.index("--cols") + 1])
    if "--input" in sys.argv:
        src_file = sys.argv[sys.argv.index("--input") + 1]

    if not os.path.exists(src_file):
        sys.exit(f"Error: {src_file} not found. Please provide an image (avatar.png or source-prepped.png).")

    img = Image.open(src_file).convert("RGBA")
    # Composite over white or transparent
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    flat = Image.alpha_composite(bg, img).convert("L")

    # A monospace cell is ~1.75x taller than wide; correct the aspect ratio
    rows = max(1, round(flat.height / flat.width * cols * (CHAR_W / CHAR_H)))
    small = flat.resize((cols, rows), Image.Resampling.LANCZOS)

    lines = []
    ramp_len = len(RAMP) - 1
    for y in range(rows):
        line_chars = []
        for x in range(cols):
            val = small.getpixel((x, y))
            idx = round((255 - val) / 255 * ramp_len)
            line_chars.append(RAMP[idx])
        lines.append("".join(line_chars).rstrip())

    w = round(cols * CHAR_W + 24)
    h = round(rows * CHAR_H + 24)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
        f'font-size="12">',
        f'<rect width="{w}" height="{h}" rx="8" fill="{BG}"/>',
        "<defs>",
    ]
    for i in range(len(lines)):
        begin = i * ROW_STAGGER
        parts.append(
            f'<clipPath id="r{i}"><rect x="0" y="0" width="0" height="{CHAR_H + 2:.1f}">'
            f'<animate attributeName="width" from="0" to="{w}" begin="{begin:.2f}s" '
            f'dur="{ROW_WIPE}s" fill="freeze"/></rect></clipPath>'
        )
    parts.append("</defs>")

    for i, line in enumerate(lines):
        if not line:
            continue
        y = 12 + (i + 1) * CHAR_H - 3
        begin = i * ROW_STAGGER
        parts.append(
            f'<g clip-path="url(#r{i})" transform="translate(12 {y - CHAR_H + 3:.1f})">'
            f'<text x="0" y="{CHAR_H - 3:.1f}" xml:space="preserve" fill="{FG}" '
            f'textLength="{len(line) * CHAR_W:.1f}">{html.escape(line)}</text></g>'
        )
        # Block cursor riding the wipe edge of this row
        parts.append(
            f'<rect x="0" y="{y - CHAR_H + 4:.1f}" width="{CHAR_W:.1f}" height="{CHAR_H:.1f}" '
            f'fill="{FG}" opacity="0">'
            f'<set attributeName="opacity" to="0.9" begin="{begin:.2f}s"/>'
            f'<animate attributeName="x" from="12" to="{w - 14}" begin="{begin:.2f}s" '
            f'dur="{ROW_WIPE}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{begin + ROW_WIPE:.2f}s"/></rect>'
        )

    parts.append("</svg>")
    out = "\n".join(parts)
    with open("ascii-portrait.svg", "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote ascii-portrait.svg ({cols}x{rows} chars, {len(out) // 1024} KiB)")


if __name__ == "__main__":
    main()
