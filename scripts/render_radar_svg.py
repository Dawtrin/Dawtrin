#!/usr/bin/env python3
"""Render data/contributions.json as an animated 360-degree Radar Calendar SVG.

Usage: python scripts/render_radar_svg.py
Writes round-radar.svg.
"""
import json
import math

BG = "#0d1117"
BORDER = "#30363d"
DIM = "#8b949e"
FG = "#c9d1d9"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

W = 860
H = 340
CX = 430
CY = 170


def main() -> None:
    with open("data/contributions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    days = data["days"]
    weeks = len(days) // 7

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="12">',
        "<style>",
        ".rc{opacity:0;animation:rcIn .6s ease-out forwards;cursor:pointer}",
        ".rc:hover{filter:brightness(1.5)}",
        "@keyframes rcIn{from{opacity:0}to{opacity:1}}",
        ".sweep{transform-origin: 430px 170px; animation: spin 4s linear infinite}",
        "@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="{BG}" stroke="{BORDER}"/>',
        f'<text x="24" y="28" fill="{FG}" font-weight="bold">Round The Year - 360° Radar Calendar</text>',
        f'<text x="{W - 24}" y="28" text-anchor="end" fill="{DIM}">52 Weeks · 7 Weekday Rings</text>',
    ]

    # Concentric background circles
    for r in range(7):
        rad = 42 + r * 15
        parts.append(f'<circle cx="{CX}" cy="{CY}" r="{rad}" fill="none" stroke="#21262d" stroke-dasharray="2,4"/>')

    # Draw cells
    for r in range(7):
        inner_r = 35 + r * 15
        outer_r = inner_r + 12
        for w in range(weeks):
            idx = w * 7 + r
            if idx >= len(days):
                continue
            d = days[idx]
            count = d["count"]
            lvl = d["level"]

            a0 = (w / weeks) * 2 * math.pi - math.pi / 2
            a1 = ((w + 0.85) / weeks) * 2 * math.pi - math.pi / 2
            delay = (w / weeks) * 1.8

            x1 = CX + outer_r * math.cos(a0)
            y1 = CY + outer_r * math.sin(a0)
            x2 = CX + outer_r * math.cos(a1)
            y2 = CY + outer_r * math.sin(a1)
            x3 = CX + inner_r * math.cos(a1)
            y3 = CY + inner_r * math.sin(a1)
            x4 = CX + inner_r * math.cos(a0)
            y4 = CY + inner_r * math.sin(a0)

            path = f"M {x1:.2f} {y1:.2f} A {outer_r} {outer_r} 0 0 1 {x2:.2f} {y2:.2f} L {x3:.2f} {y3:.2f} A {inner_r} {inner_r} 0 0 0 {x4:.2f} {y4:.2f} Z"
            tip = f"{count} contributions on {d['date']}"
            parts.append(
                f'<path class="rc" style="animation-delay:{delay:.3f}s" d="{path}" fill="{PALETTE[lvl]}">'
                f'<title>{tip}</title></path>'
            )

    # Radar Sweep Hand
    parts.append(
        f'<g class="sweep">'
        f'<line x1="{CX}" y1="{CY}" x2="{CX}" y2="{CY - 145}" stroke="#69f0a0" stroke-width="2" opacity="0.7"/>'
        f'<circle cx="{CX}" cy="{CY - 145}" r="3.5" fill="#69f0a0"/>'
        f'</g>'
    )
    # Center core
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="22" fill="#161b22" stroke="{BORDER}"/>')
    parts.append(f'<text x="{CX}" y="{CY + 4}" text-anchor="middle" fill="{FG}" font-size="10" font-weight="bold">365D</text>')

    parts.append("</svg>")

    with open("round-radar.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("wrote round-radar.svg")


if __name__ == "__main__":
    main()
