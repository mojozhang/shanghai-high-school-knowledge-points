#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 Chrome 无头模式把 HTML 直接打印成 PDF —— 与网页排版完全一致（MathJax 公式）。"""
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = ROOT / "输出" / "上海高中物理知识图谱.html"
PDF = ROOT / "输出" / "上海高中物理知识图谱手册.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def main():
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
        "--virtual-time-budget=120000", f"--print-to-pdf={PDF}",
        HTML.as_uri(),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("pdf:", PDF.exists(), PDF.stat().st_size)

if __name__ == "__main__":
    main()
