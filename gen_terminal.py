#!/usr/bin/env python3
"""Generate terminal.svg: a terminal session that draws an ASCII iPhone.

Usage: gen_terminal.py OUT.svg [--static]
Every character is placed at an explicit x so the grid stays aligned
whatever monospace font the viewer has.
"""
import sys
from html import escape

CW, LH, FS = 8.4, 17, 14          # cell width, line height, font size
PAD_X, BAR_H, PAD_TOP = 22, 34, 20
INNER = 20                         # phone screen width in cells

# ---- phone screen: rows of (text, class) segments -------------------------
K, S, T, N, D, G, F = "k", "s", "t", "n", "d", "g", "f"
screen = [
    [("  9:41   ", F), ("━━━━", D), ("    5G", F)],
    [],
    [(" ", F), ("struct", K), (" ", F), ("Tudor", T), (" {", F)],
    [("   ", F), ("let", K), (" lang =", F)],
    [("     ", F), ('"Swift"', S)],
    [("   ", F), ("let", K), (" ai =", F)],
    [("     ", F), ("Model", T), (".onDevice", F)],
    [("   ", F), ("let", K), (" network =", F)],
    [("     ", F), (".optional", F)],
    [("   ", F), ("let", K), (" apps = ", F), ("29", N)],
    [(" }", F)],
    [],
    [(" ", F), ("✓ Build succeeded", G)],
    [("   0 warnings", D)],
    [("   0 errors", D)],
    [],
    [("      ", F), ("━━━━━━━━", D)],
]

phone = [[("╭" + "─" * INNER + "╮", "b")]]
for segs in screen:
    width = sum(len(t) for t, _ in segs)
    assert width <= INNER, (width, segs)
    phone.append([("│", "b")] + segs + [(" " * (INNER - width), F), ("│", "b")])
phone.append([("╰" + "─" * INNER + "╯", "b")])

# ---- neofetch-style info ---------------------------------------------------
info = [
    [("tudor", "h"), ("@", F), ("luzern", "h")],
    [("────────────", D)],
    [("role      ", "l"), ("iOS tech lead, indie dev", F)],
    [("os        ", "l"), ("iOS · macOS · watchOS · visionOS", F)],
    [("lang      ", "l"), ("Swift · C++ · Python", F)],
    [("ai        ", "l"), ("MLX · whisper.cpp", F)],
    [("focus     ", "l"), ("on-device, offline-first", F)],
    [("shipped   ", "l"), ("29 apps on the App Store", F)],
    [("oss       ", "l"), ("SkillHub · Portly", F)],
    [("uptime    ", "l"), ("10+ years", F)],
    [("backend   ", "l"), ("Vapor · FastAPI", F)],
]
SWATCHES = ["#ff7b72", "#f0883e", "#e3b341", "#3fb950", "#58a6ff", "#bc8cff", "#8b949e", "#f0f6fc"]

COMMAND = "xcrun simctl boot tudor && neofetch"
PHONE_COL, INFO_COL = 0, INNER + 2 + 3
PHONE_ROW, INFO_ROW = 2, 4

cols = INFO_COL + max(sum(len(t) for t, _ in line) for line in info)
rows = PHONE_ROW + len(phone) + 2
W = round(PAD_X * 2 + cols * CW)
H = BAR_H + PAD_TOP + rows * LH + 8


def x_of(col):
    return PAD_X + col * CW


def y_of(row):
    return BAR_H + PAD_TOP + row * LH + FS - 3


def run(segs, col, row):
    """Emit one <text> per colour class, each glyph pinned to its cell."""
    out = []
    for text, cls in segs:
        cells = [(col + i, ch) for i, ch in enumerate(text) if ch != " "]
        if cells:
            xs = " ".join(f"{x_of(c):.1f}" for c, _ in cells)
            chars = escape("".join(ch for _, ch in cells))
            out.append(f'<text class="{cls}" x="{xs}" y="{y_of(row)}">{chars}</text>')
        col += len(text)
    return "".join(out)


def group(body, delay):
    return f'<g class="a" style="animation-delay:{delay:.2f}s">{body}</g>'


static = "--static" in sys.argv
parts = []

# typed command
parts.append(group(run([("$", "g")], 0, 0), 0.3))
t = 0.7
for i, ch in enumerate(COMMAND):
    if ch != " ":
        parts.append(group(run([(ch, F)], 2 + i, 0), t))
    t += 0.045
t += 0.35

# phone, top to bottom
for i, segs in enumerate(phone):
    parts.append(group(run(segs, PHONE_COL, PHONE_ROW + i), t + i * 0.07))

# info lines and colour swatches
for i, segs in enumerate(info):
    parts.append(group(run(segs, INFO_COL, INFO_ROW + i), t + 0.25 + i * 0.11))
sw_row = INFO_ROW + len(info) + 1
sw = "".join(
    f'<rect x="{x_of(INFO_COL) + i * CW * 3:.1f}" y="{y_of(sw_row) - FS + 2}" '
    f'width="{CW * 3:.1f}" height="{LH}" fill="{c}"/>'
    for i, c in enumerate(SWATCHES)
)
parts.append(group(sw, t + 0.25 + (len(info) + 1) * 0.11))

# closing prompt with a blinking cursor
end = t + len(phone) * 0.07 + 0.3
last = PHONE_ROW + len(phone) + 1
cursor = (
    f'<rect class="cur" x="{x_of(2):.1f}" y="{y_of(last) - FS + 2}" '
    f'width="{CW:.1f}" height="{LH - 1}"/>'
)
parts.append(group(run([("$", "g")], 0, last) + cursor, end))

anim = "" if static else """
  .a { animation: in .01s linear both; }
  .cur { animation: blink 1.1s steps(1) infinite; }
  @keyframes in { from { opacity: 0 } to { opacity: 1 } }
  @keyframes blink { 50% { opacity: 0 } }
  @media (prefers-reduced-motion: reduce) { .a, .cur { animation: none } }"""

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">Terminal session drawing an iPhone in text characters</title>
<desc id="d">The command xcrun simctl boot tudor &amp;&amp; neofetch prints an iPhone whose screen shows a Swift struct, beside a summary: iOS tech lead and indie dev; Swift, C++ and Python; on-device and offline-first AI; 29 apps on the App Store; Vapor and FastAPI on the backend.</desc>
<style>
  text {{ font: {FS}px ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; white-space: pre; }}
  .f {{ fill: #e6edf3 }} .d {{ fill: #8b949e }} .b {{ fill: #6e7681 }}
  .k {{ fill: #ff7b72 }} .s {{ fill: #a5d6ff }} .t {{ fill: #d2a8ff }}
  .n {{ fill: #79c0ff }} .g {{ fill: #3fb950 }} .l {{ fill: #58a6ff; font-weight: 600 }}
  .h {{ fill: #f0883e; font-weight: 600 }} .cur {{ fill: #e6edf3 }}{anim}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
<path d="M.5 {BAR_H}.5h{W - 1}" stroke="#30363d"/>
<circle cx="20" cy="17" r="6" fill="#ff5f57"/><circle cx="40" cy="17" r="6" fill="#febc2e"/><circle cx="60" cy="17" r="6" fill="#28c840"/>
<text class="d" x="{W / 2}" y="22" text-anchor="middle">tudor@luzern: ~</text>
{chr(10).join(parts)}
</svg>
"""
open(sys.argv[1], "w").write(svg)
print(f"{sys.argv[1]}: {W}x{H}, {len(svg)} bytes, {cols} cols x {rows} rows")
