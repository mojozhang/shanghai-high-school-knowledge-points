#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""预渲染所有公式到 图/公式/ 缓存（用系统 python，带 matplotlib）。"""
import pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mathfmt

ROOT = pathlib.Path(__file__).resolve().parent.parent
n = 0
for f in sorted(ROOT.glob("*.md")):
    if not f.name[:2].isdigit():
        continue
    for line in f.read_text(encoding="utf-8").splitlines():
        for a, b, frag in mathfmt.spans(line):
            if mathfmt.render(frag): n += 1
        s = line.strip()
        if s.startswith("|"):
            for cell in s.strip("|").split("|"):
                c = cell.strip().replace("**", "")
                if mathfmt.is_formula(c) and mathfmt.render(c): n += 1
print("rendered", n)
