#!/bin/bash
# 一键重建全部交付物：MD → JSON → Excel / Word / PDF / HTML
set -e
cd "$(dirname "$0")/.."

PY=python3
DOCX_PY=/Users/mojozhang/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3

echo "== 1/4 解析 Markdown =="
$PY build/parse.py

echo "== 2/4 生成 Excel =="
$DOCX_PY build/gen_xlsx.py

echo "== 3/5 生成 Word =="
DSH_SKIP_PDF=1 $DOCX_PY build/gen_docx.py

echo "== 4/5 生成 HTML 图谱 =="
$PY build/gen_html.py

echo "== 5/5 打印 PDF（Chrome，公式与网页一致）=="
$PY build/gen_pdf.py

echo
echo "输出目录："
ls -lh 输出/
