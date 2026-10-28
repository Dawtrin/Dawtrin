#!/usr/bin/env python3
"""Render data/contributions.json as an animated 3D isometric Skyline SVG.

Usage: python scripts/render_skyline_svg.py
Writes skyline-3d.svg.
"""
import json
import math

BG = "#0d1117"
BORDER = "#30363d"
DIM = "#8b949e"
FG = "#c9d1d9"
ACCENT = "#58a6ff"

PALETTE_FRONT = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#57ab5a"]
PALETTE_TOP = ["#21262d", "#26a641", "#39d353", "#56d364", "#7ee787", "#aff5b4"]
PALETTE_SIDE = ["#0d1117", "#052614", "#004d23", "#196c2e", "#238636", "#2ea043"]

W = 860
H = 260
OX = 45
OY = 205
STEP_X = 14
STEP_Y = 6


def main() -> None:
    with open("data/contributions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    days = data["days"]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="12">',
        "<style>",
        ".b{transform-box:fill-box;transform-origin:bottom;animation:rise .6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;opacity:0}",
        ".b:hover rect, .b:hover polygon{filter:brightness(1.3);cursor:pointer}",
        "@keyframes rise{from{opacity:0;transform:scaleY(0)}to{opacity:1;transform:scaleY(1)}}",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="{BG}" stroke="{BORDER}"/>',
        # Title
        f'<text x="24" y="28" fill="{FG}" font-weight="bold">3D Skyline - Commit City</text>',
        f'<text x="{W - 24}" y="28" text-anchor="end" fill="{DIM}">{data["total"]:,} contributions</text>',
    ]

    max_day = {"count": 0, "x": 0, "y": 0, "h": 0, "date": ""}
    weeks = len(days) // 7

    # Draw back to front (row 0 to 6)
    for r in range(7):
        for col in range(weeks):
            idx = col * 7 + r
            if idx >= len(days):
                continue
            d = days[idx]
            count = d["count"]
            lvl = d["level"]

            # Height based on sqrt(count)
            base_h = 4 if lvl == 0 else 12 + int(math.sqrt(count) * 24)
            x = OX + col * STEP_X - r * 4
            y = OY + r * STEP_Y
            delay = (col + r * 2) * 0.012

            if count > max_day["count"]:
                max_day = {"count": count, "x": x + 5, "y": y - base_h, "h": base_h, "date": d["date"]}

            tip = f"{count} contributions on {d['date']}"
            f_col = PALETTE_FRONT[lvl]
            t_col = PALETTE_TOP[lvl]
            s_col = PALETTE_SIDE[lvl]

            # Building group with CSS animation
            group = [
                f'<g class="b" style="animation-delay:{delay:.3f}s">',
                f'<title>{tip}</title>',
                # Front Face
                f'<rect x="{x}" y="{y - base_h}" width="10" height="{base_h}" fill="{f_col}"/>',
                # Top Face
                f'<polygon points="{x},{y - base_h} {x + 4},{y - base_h - 4} {x + 14},{y - base_h - 4} {x + 10},{y - base_h}" fill="{t_col}"/>',
                # Side Face
                f'<polygon points="{x + 10},{y - base_h} {x + 14},{y - base_h - 4} {x + 14},{y - 4} {x + 10},{y}" fill="{s_col}"/>',
                '</g>'
            ]
            parts.extend(group)

    # Leader line for best day
    if max_day["count"] > 0:
        bx = max_day["x"]
        by = max_day["y"]
        callout_x = min(bx + 40, W - 180)
        callout_y = max(by - 35, 45)
        parts.append(
            f'<g class="b" style="animation-delay:0.9s">'
            f'<polyline points="{bx},{by} {bx},{callout_y} {callout_x},{callout_y}" fill="none" stroke="{ACCENT}" stroke-width="1.5"/>'
            f'<circle cx="{bx}" cy="{by}" r="2.5" fill="{ACCENT}"/>'
            f'<text x="{callout_x + 6}" y="{callout_y + 4}" fill="#ffffff" font-size="11">Peak: {max_day["count"]} commits ({max_day["date"]})</text>'
            f'</g>'
        )

    parts.append("</svg>")

    with open("skyline-3d.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("wrote skyline-3d.svg")


if __name__ == "__main__":
    main()
