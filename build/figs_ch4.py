#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单元三（牛顿运动定律）配图：电梯超重、连接体、传送带、板块。"""
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


def ground(x1, x2, y, step=18):
    s = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#333" stroke-width="2.5"/>'
    x = x1
    while x < x2 - 4:
        s += f'<line x1="{x}" y1="{y}" x2="{x - 9}" y2="{y + 12}" stroke="#9ca3af" stroke-width="1"/>'
        x += step
    return s


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

# ---------- 电梯超重 ----------
b = '<rect x="150" y="55" width="170" height="185" fill="#f7f9fb" stroke="#333" stroke-width="2"/>'
b += '<line x1="235" y1="55" x2="235" y2="30" stroke="#333" stroke-width="2"/>'
b += '<rect x="216" y="140" width="38" height="72" fill="#ffffff" stroke="#333" stroke-width="2"/>'
b += arrow(235, 140, 235, 98, "gray", "N", 243, 106)
b += arrow(235, 212, 235, 248, "red", "G", 243, 236)
b += arrow(330, 190, 330, 130, "blue", "a", 338, 168, dash=True)
b += label(16, 40, "加速上升：N ＞ G，视重变大（超重）", "gray", 12)
figs["A-4.5-L-4.5-1"] = wrap(b, "图 L-4.5-1　电梯超重（a 向上）")

# ---------- 连接体 ----------
b = ground(70, 420, 215)
b += '<rect x="115" y="150" width="72" height="65" fill="#f6f6f2" stroke="#333" stroke-width="2"/>'
b += label(140, 190, "m₁")
b += '<rect x="255" y="150" width="72" height="65" fill="#eef2f7" stroke="#333" stroke-width="2"/>'
b += label(280, 190, "m₂")
b += '<line x1="187" y1="182" x2="255" y2="182" stroke="#333" stroke-width="2"/>'
b += arrow(327, 182, 405, 182, "blue", "F", 360, 172)
b += label(16, 40, "两物块用绳连接，整体加速度相同", "gray", 12)
figs["A-4.6-L-4.6-2"] = wrap(b, "图 L-4.6-2　连接体：先整体求 a，再隔离求绳力")

# ---------- 传送带 ----------
b = '<circle cx="150" cy="185" r="24" fill="#ffffff" stroke="#333" stroke-width="2"/>'
b += '<circle cx="345" cy="185" r="24" fill="#ffffff" stroke="#333" stroke-width="2"/>'
b += '<line x1="150" y1="161" x2="345" y2="161" stroke="#333" stroke-width="2.5"/>'
b += '<line x1="150" y1="209" x2="345" y2="209" stroke="#333" stroke-width="2.5"/>'
b += '<rect x="215" y="131" width="52" height="30" fill="#f6f6f2" stroke="#333" stroke-width="2"/>'
b += arrow(300, 115, 380, 115, "blue", "带速 v", 330, 106)
b += arrow(272, 152, 340, 152, "green", "f", 298, 144)
b += label(16, 40, "物块初速为零，带向右运动：摩擦力向右，是动力", "gray", 12)
figs["A-4.8-L-4.8-1"] = wrap(b, "图 L-4.8-1　水平传送带：摩擦力可以是动力")

# ---------- 板块 ----------
b = ground(60, 430, 235)
b += '<rect x="100" y="180" width="290" height="42" fill="#eef2f7" stroke="#333" stroke-width="2"/>'
b += label(112, 208, "长木板 M")
b += '<rect x="200" y="136" width="64" height="44" fill="#ffffff" stroke="#333" stroke-width="2"/>'
b += label(214, 164, "m")
b += arrow(268, 158, 340, 158, "blue", "v₀", 300, 150)
b += arrow(200, 176, 150, 176, "green", "f", 158, 168)
b += arrow(264, 176, 314, 176, "orange", "f′", 288, 168)
b += label(16, 40, "物块滑上木板：两者加速度不同，直到共速", "gray", 12)
figs["A-4.9-L-4.9-1"] = wrap(b, "图 L-4.9-1　板块模型：摩擦力让木板也动起来")

for name, svg in figs.items():
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
    print("written", name)
