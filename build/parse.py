#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把知识卡 Markdown 解析成结构化 JSON —— 全套交付物的唯一数据源。

用法：
    python3 build/parse.py          # 生成 data/考点库.json
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "考点库.json"

CARD_RE = re.compile(r"^## ([A-N]-\d+(?:\.\d+)?)\s+(.+?)\s*$")
SEC_RE = re.compile(r"^### (.+?)\s*$", re.M)
H2_RE = re.compile(r"^## (.+?)\s*$", re.M)
UNIT_RE = re.compile(r"^# (.+?)\s*$", re.M)
EX_RE = re.compile(r"^例题\s*(\d)\s*[·・]?\s*(L\d)?\s*(.*)$")


def parse_table(lines):
    """把连续的 | ... | 行解析成二维数组（去掉分隔行）。"""
    rows = []
    for ln in lines:
        s = ln.strip().replace("\\|", "｜")
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(set(c) <= set("-: ") and c for c in cells):
            continue
        rows.append(cells)
    return rows


def tables_in(text):
    """提取文本中所有表格（按空行/非表格行分块）。"""
    out, buf = [], []
    for ln in text.splitlines():
        if ln.strip().startswith("|"):
            buf.append(ln)
        else:
            if len(buf) >= 2:
                out.append(parse_table(buf))
            buf = []
    if len(buf) >= 2:
        out.append(parse_table(buf))
    return out


def clean(s):
    return re.sub(r"\s+", " ", s).strip()


def split_sections(block):
    parts = SEC_RE.split(block)
    secs = []
    for i in range(1, len(parts), 2):
        secs.append({"title": clean(parts[i]), "body": parts[i + 1].strip()})
    return secs


def parse_card(cid, name, block, unit_title, fname):
    meta = ""
    for ln in block.splitlines():
        s = ln.strip()
        if s.startswith("*") and s.endswith("*") and len(s) > 2:
            meta = s.strip("*")
            break
    req = "Ⅱ" if "Ⅱ" in meta else ("Ⅰ" if "Ⅰ" in meta else "")
    freq = ""
    m = re.search(r"考频\s*\**\s*([高中低])", meta)
    if m:
        freq = m.group(1)
    star = "★" if "★" in meta else ""

    guess = ""
    m = re.search(r"\*\*⚡ 先猜\*\*[：:]\s*(.+)", block)
    if m:
        guess = clean(m.group(1))

    secs = split_sections(block)
    examples = []
    for s in secs:
        m = EX_RE.match(s["title"])
        if not m:
            continue
        body = s["body"]
        problem = re.split(r"\*\*解析\*\*", body)[0].strip()
        examples.append({
            "n": int(m.group(1)),
            "level": m.group(2) or "",
            "title": clean(m.group(3)),
            "problem": clean(problem)[:120],
            "body": body,
        })

    return {
        "id": cid,
        "name": clean(name),
        "unit": unit_title,
        "file": fname,
        "meta": meta,
        "req": req,
        "freq": freq,
        "star": star,
        "guess": guess,
        "sections": secs,
        "examples": examples,
        "body": block.strip(),
    }


def parse_unit(path):
    text = path.read_text(encoding="utf-8")
    m = UNIT_RE.search(text)
    unit_title = clean(m.group(1)) if m else path.stem

    heads = list(H2_RE.finditer(text))
    cards, extras = [], []
    for i, h in enumerate(heads):
        title = clean(h.group(1))
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        block = text[h.end():end]
        cm = CARD_RE.match("## " + title)
        if cm:
            cards.append(parse_card(cm.group(1), cm.group(2), block, unit_title, path.name))
        else:
            extras.append({"title": title, "body": block.strip()})

    formulas, relations, levels = [], [], []
    for ex in extras:
        if "公式" in ex["title"]:
            for tb in tables_in(ex["body"]):
                for row in tb[1:]:
                    if len(row) >= 4 and row[0].strip().isdigit():
                        formulas.append({"unit": unit_title, "no": row[0], "formula": row[1],
                                         "meaning": row[2], "cond": row[3]})
        if "关系" in ex["title"]:
            for tb in tables_in(ex["body"]):
                for row in tb[1:]:
                    if len(row) >= 3 and re.match(r"^[A-N]-\d", row[0]):
                        relations.append({"from": row[0], "to": row[1], "type": row[2]})
        if "关卡" in ex["title"]:
            for tb in tables_in(ex["body"]):
                for row in tb[1:]:
                    if len(row) >= 4:
                        levels.append({"no": row[0], "name": row[1], "diff": row[2], "star": row[3]})

    return {"title": unit_title, "file": path.name, "cards": cards,
            "formulas": formulas, "relations": relations, "levels": levels,
            "extras": extras}


def main():
    files = []
    for p in sorted(ROOT.glob("*.md")):
        if "单元" in p.name and "闯关" not in p.name:
            if len(re.findall(r"^## [A-N]-\d+(?:\.\d+)?", p.read_text(encoding="utf-8"), re.M)) >= 3:
                files.append(p)
    units = [parse_unit(p) for p in files]
    data = {
        "units": units,
        "stats": {
            "units": len(units),
            "cards": sum(len(u["cards"]) for u in units),
            "examples": sum(len(c["examples"]) for u in units for c in u["cards"]),
            "formulas": sum(len(u["formulas"]) for u in units),
        },
        "files": [u["file"] for u in units],
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    s = data["stats"]
    print(f"units={s['units']} cards={s['cards']} examples={s['examples']} formulas={s['formulas']}")
    for u in units:
        print(f"  - {u['file']}: {len(u['cards'])} cards, {sum(len(c['examples']) for c in u['cards'])} examples")


if __name__ == "__main__":
    main()
