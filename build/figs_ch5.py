#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单元四（曲线运动）配图：平抛分解、竖直圆最高点、转弯受力。"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "图"
OUT.mkdir(exist_ok=True)

COLORS = {"red": "#c0392b", "blue": "#1f6feb", "green": "#1a7f37",
          "gray": "#6b7280", "orange": "#b45309", "ink": "#333333"}
MARKERS = "".join(
    f'<marker id="m-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
    f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
    f'fill="{v}"/></marker>' for k, v in COLORS.items())


def arrow(x1, y1, x2, y2, color, label="", lx=0, ly=0, dash=False, fs=13):
    d = ' stroke-dasharray="6 4"' if dash else ""
    s = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{COLORS[color]}" '
         f'stroke-width="2"{d} marker-end="url(#m-{color})"/>')
    if label:
        s += f'<text x="{lx}" y="{ly}" fill="{COLORS[color]}" font-size="{fs}">{label}</text>'
    return s


def label(x, y, t, color="ink", fs=13, anchor="start", weight="normal"):
    return (f'<text x="{x}" y="{y}" fill="{COLORS.get(color, color)}" font-size="{fs}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{t}</text>')


def wrap(body, title):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 280" width="480" height="280" '
        'font-family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif" font-size="13">\n'
        f'<defs>{MARKERS}</defs>\n'
        '<rect width="480" height="280" fill="#ffffff"/>\n'
        '<rect x="0.5" y="0.5" width="479" height="279" fill="none" stroke="#e5e7eb"/>\n'
        f'{label(16, 26, title, "ink", 13, "start", "600")}\n'
        f'{body}\n</svg>\n')


figs = {}

# ---------- 平抛：速度分解 ----------
b = '<line x1="70" y1="70" x2="440" y2="70" stroke="#9ca3af" stroke-width="1" stroke-dasharray="5 5"/>'
b += '<line x1="70" y1="60" x2="70" y2="250" stroke="#333" stroke-width="2"/>'
b += '<line x1="70" y1="70" x2="440" y2="70" stroke="#333" stroke-width="2"/>'
b += label(444, 74, "x", "ink", 12)
b += label(58, 250, "y", "ink", 12)
b += '<path d="M70,70 Q240,70 400,230" fill="none" stroke="#333" stroke-width="2"/>'
b += arrow(70, 70, 150, 70, "blue", "v₀", 96, 60)
b += '<circle cx="330" cy="176" r="4" fill="#c0392b"/>'
b += arrow(330, 176, 400, 176, "blue", "vx", 356, 168)
b += arrow(330, 176, 330, 240, "red", "vy", 338, 212)
b += arrow(330, 176, 384, 230, "orange", "v", 392, 214)
b += label(150, 108, "水平：匀速", "gray", 11)
b += label(96, 206, "竖直：自由落体", "gray", 11)
figs["A-5.3-L-5.3-2"] = wrap(b, "图 L-5.3-2　平抛：水平匀速 + 竖直自由落体")

# ---------- 竖直圆最高点 ----------
b = '<circle cx="240" cy="158" r="88" fill="none" stroke="#333" stroke-width="2"/>'
b += '<circle cx="240" cy="70" r="14" fill="#ffffff" stroke="#333" stroke-width="2"/>'
b += arrow(228, 82, 228, 128, "red", "mg", 200, 108)
b += arrow(252, 82, 252, 150, "blue", "T", 260, 130)
b += label(272, 74, "v", "ink", 12)
b += label(96, 268, "最高点：mg 与 T 都指向圆心，mg + T = mv²/r", "gray", 11)
figs["A-5.8-L-5.8-1"] = wrap(b, "图 L-5.8-1　绳模型最高点受力")

# ---------- 转弯（俯视图） ----------
b = '<circle cx="240" cy="150" r="100" fill="none" stroke="#b9c2bd" stroke-width="1.5" stroke-dasharray="6 6"/>'
b += '<line x1="240" y1="150" x2="240" y2="250" stroke="#9ca3af" stroke-width="1" stroke-dasharray="4 4"/>'
b += '<rect x="212" y="238" width="56" height="26" fill="#ffffff" stroke="#333" stroke-width="2"/>'
b += arrow(268, 251, 356, 251, "blue", "v", 312, 243)
b += arrow(240, 238, 240, 182, "green", "", 0, 0)
b += label(214, 214, "f", "green", 12)
b += label(252, 196, "f = mv²/r", "green", 11)
b += label(252, 128, "O", "ink", 12)
b += label(96, 272, "汽车转弯：静摩擦力提供向心力，指向圆心", "gray", 11)
figs["A-5.6-L-5.6-1"] = wrap(b, "图 L-5.6-1　汽车转弯（俯视图）")

for name, svg in figs.items():
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
    print("written", name)
