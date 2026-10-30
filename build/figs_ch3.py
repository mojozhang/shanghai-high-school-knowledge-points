#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成第3章（相互作用与物体平衡）母题示意图 SVG。

图形规范见 00-体例与符号规范.md 第九节：
  画布 480×280，线宽 2，字号 13，中文标签，
  红色=重力 G，蓝色=绳/杆的力或外力 F，绿色=摩擦力 f，灰色=支持力 N，橙色=特殊力。
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "图"
OUT.mkdir(exist_ok=True)

COLORS = {
    "red": "#c0392b", "blue": "#1f6feb", "green": "#1a7f37",
    "gray": "#6b7280", "orange": "#b45309", "ink": "#333333",
}
MARKERS = "".join(
    f'<marker id="m-{k}" viewBox="0 0 10 10" refX="9" refY="5" '
    f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{v}"/></marker>'
    for k, v in COLORS.items()
)


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
        f'{body}\n</svg>\n'
    )


figs = {}

# ---------- M-3.1 重力方向 ----------
b = ground(50, 440, 232)
b += '<polygon points="90,232 90,70 400,232" fill="#f6f6f2" stroke="#333" stroke-width="2"/>'
b += '<circle cx="259" cy="132" r="20" fill="#ffffff" stroke="#333" stroke-width="2"/>'
b += arrow(259, 132, 259, 224, "red", "G 竖直向下 ✓", 266, 210)
b += arrow(259, 132, 234, 181, "gray", "垂直斜面 ✗", 118, 200, dash=True)
b += label(60, 60, "同一物体：重力方向恒定，与斜面倾角无关", "gray", 12)
figs["A-3.1-M-3.1"] = wrap(b, "图 M-3.1　重力方向与重心")

# ---------- M-3.2 弹簧与 F-x 图 ----------
b = '<line x1="60" y1="46" x2="215" y2="46" stroke="#333" stroke-width="4"/>'
b += ('<polyline points="135,46 121,56 149,66 121,76 149,86 121,96 149,106 135,116" '
      'fill="none" stroke="#333" stroke-width="2"/>')
b += '<rect x="110" y="116" width="50" height="40" fill="#f6f6f2" stroke="#333" stroke-width="2"/>'
b += label(126, 142, "m")
b += arrow(135, 156, 135, 210, "red", "G", 143, 196)
b += label(160, 92, "x = 形变量", "gray", 12)
b += '<line x1="260" y1="205" x2="452" y2="205" stroke="#333" stroke-width="2"/>'
b += '<line x1="260" y1="205" x2="260" y2="58" stroke="#333" stroke-width="2"/>'
b += arrow(260, 205, 452, 205, "ink")
b += arrow(260, 205, 260, 58, "ink")
b += label(456, 209, "x", "ink", 13)
b += label(246, 52, "F", "ink", 13)
b += label(238, 222, "0", "ink", 12)
b += '<line x1="260" y1="205" x2="420" y2="88" stroke="#1f6feb" stroke-width="2"/>'
b += label(398, 128, "F = kx", "blue", 13)
figs["A-3.2-M-3.2"] = wrap(b, "图 M-3.2　胡克定律 F = kx（x 为形变量）")

# ---------- M-3.3 静摩擦与滑动摩擦 ----------
b = ground(60, 430, 215)
b += '<rect x="185" y="140" width="90" height="75" fill="#f6f6f2" stroke="#333" stroke-width="2"/>'
b += label(196, 200, "m = 2 kg")
b += arrow(276, 178, 376, 178, "blue", "F = 5 N", 300, 168)
b += arrow(184, 178, 96, 178, "green", "f = 5 N", 104, 168)
b += arrow(206, 139, 206, 86, "gray", "N", 214, 104)
b += arrow(255, 215, 255, 258, "red", "G = 20 N", 262, 248)
b += label(60, 46, "最大静摩擦 7 N ＞ 滑动摩擦 6 N", "gray", 12)
figs["A-3.3-M-3.3"] = wrap(b, "图 M-3.3　水平面上的静摩擦与滑动摩擦")

# ---------- M-3.4 力的合成 ----------
b += arrow(110, 220, 310, 220, "blue", "F₁ = 30 N", 190, 243)
b += arrow(110, 220, 110, 80, "orange", "F₂ = 40 N", 66, 150)
b += '<line x1="310" y1="220" x2="310" y2="80" stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="6 4"/>'
b += '<line x1="110" y1="80" x2="310" y2="80" stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="6 4"/>'
b += arrow(110, 220, 310, 80, "red", "F = 50 N", 318, 152)
b += '<path d="M110,206 L124,206 L124,220" fill="none" stroke="#333" stroke-width="1.5"/>'
figs["A-3.4-M-3.4"] = wrap(b, "图 M-3.4　平行四边形定则（夹角 90°）")

# ---------- M-3.5 斜面上的三力平衡 ----------
b = '<polygon points="90,230 330,230 90,49" fill="#f6f6f2" stroke="#333" stroke-width="2"/>'
b += '<g transform="rotate(37 249 147)"><rect x="217" y="130" width="64" height="34" fill="#ffffff" stroke="#333" stroke-width="2"/></g>'
b += arrow(150, 147, 212, 147, "blue", "F", 156, 138)
b += arrow(249, 147, 285, 99, "gray", "N", 292, 94)
b += arrow(249, 147, 249, 232, "red", "G", 257, 205)
b += label(298, 222, "37°", "ink", 13)
b += label(60, 38, "无摩擦，水平力 F 把物体压住", "gray", 12)
figs["A-3.5-M-3.5"] = wrap(b, "图 M-3.5　斜面上受水平力的三力平衡")

# ---------- M-3.6 动态平衡：绳偏角固定 ----------
b = '<line x1="140" y1="50" x2="360" y2="50" stroke="#333" stroke-width="4"/>'
b += '<line x1="250" y1="50" x2="334" y2="162" stroke="#333" stroke-width="2"/>'
b += '<line x1="250" y1="50" x2="250" y2="180" stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="6 4"/>'
b += '<circle cx="334" cy="162" r="18" fill="#ffffff" stroke="#333" stroke-width="2"/>'
b += arrow(334, 162, 292, 106, "blue", "T", 294, 122)
b += arrow(352, 162, 416, 162, "orange", "F", 396, 152)
b += arrow(334, 162, 334, 240, "red", "G", 342, 216)
b += arrow(334, 162, 390, 120, "gray", "F 最小", 392, 114, dash=True, fs=11)
b += label(304, 92, "37°", "ink", 12)
figs["A-3.6-M-3.6"] = wrap(b, "图 M-3.6　绳偏角固定时拉力的最小值")

# ---------- M-3.7 整体法与隔离法 ----------
b = ground(70, 410, 230)
b += '<rect x="165" y="170" width="130" height="60" fill="#eef2f7" stroke="#333" stroke-width="2"/>'
b += label(196, 206, "B  1 kg")
b += '<rect x="190" y="120" width="80" height="50" fill="#ffffff" stroke="#333" stroke-width="2"/>'
b += label(200, 152, "A  2 kg")
b += arrow(296, 200, 372, 200, "blue", "F = 9 N", 300, 190)
b += arrow(270, 145, 322, 145, "green", "f", 328, 150)
b += label(78, 258, "地面光滑；A、B 间 μ = 0.5", "gray", 12)
figs["A-3.7-M-3.7"] = wrap(b, "图 M-3.7　叠放体的整体法与隔离法")

# ---------- M-3.8 斜面临界 ----------
b = '<polygon points="90,230 350,230 90,80" fill="#f6f6f2" stroke="#333" stroke-width="2"/>'
b += '<g transform="rotate(30 242 148)"><rect x="208" y="132" width="68" height="32" fill="#ffffff" stroke="#333" stroke-width="2"/></g>'
b += arrow(242, 148, 272, 96, "gray", "N", 280, 92)
b += arrow(242, 148, 194, 120, "green", "f", 176, 112)
b += arrow(242, 148, 242, 236, "red", "G", 250, 208)
b += label(336, 224, "θ", "ink", 13)
b += label(60, 42, "恰好静止 ⇔ tanθ = μ", "gray", 12)
figs["A-3.8-M-3.8"] = wrap(b, "图 M-3.8　斜面临界：恰好不下滑")

for name, svg in figs.items():
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
    print("written", name, len(svg))
