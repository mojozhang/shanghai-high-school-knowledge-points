#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 data/考点库.json 生成单文件交互式图谱：输出/上海高中物理知识图谱.html

特性：离线可用（图片 base64 内联）、左侧树 + 搜索、图谱视图（SVG 节点与关系边）、
      点击节点跳转卡片、按关系类型着色、支持打印。
"""
import base64
import sys
import json
import pathlib
import re

import markdown

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mathfmt

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "考点库.json"
OUT = ROOT / "输出" / "上海高中物理知识图谱.html"

TYPE_COLOR = {"前置": "#0b6b5b", "派生": "#1f6feb", "综合": "#b45309",
              "易错": "#c0392b", "实验": "#6b7280", "延伸": "#7c3aed",
              "工具": "#0891b2", "应用": "#db2777", "特例": "#6b7280",
              "图像法": "#1f6feb"}


def inline_svg(html):
    """把 图/ 下的所有图片（svg/png/jpg）内联成 data URI，单文件离线可用。"""
    MIME = {".svg": "image/svg+xml", ".png": "image/png",
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}

    def rep(m):
        p = ROOT / m.group(1)
        if not p.exists():
            return m.group(0)
        mime = MIME.get(p.suffix.lower(), "image/png")
        b64 = base64.b64encode(p.read_bytes()).decode()
        return 'src="data:%s;base64,%s"' % (mime, b64)

    return re.sub(r'src="(图/[^"]+)"', rep, html)



def fmt_html(md_text):
    r"""把公式片段包成 \(...\)，交给 MathJax 排版（整段表达式，不再切碎）。"""
    pos, out = 0, []
    for a, b, frag in mathfmt.spans(md_text, whole=True):
        out.append(md_text[pos:a])
        try:
            out.append("\\(" + mathfmt.to_latex(frag) + "\\)")
        except Exception:
            out.append(frag)
        pos = b
    out.append(md_text[pos:])
    return "".join(out)


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    cards, edges, units = [], [], []
    pos = {}
    for ui, u in enumerate(d["units"]):
        m = re.search(r"单元([一二三四五六七八九十]+)", u["title"])
        chap = re.search(r"第\s*(\d+)\s*章", u["title"])
        short = ("单元" + m.group(1) if m else u["title"][:6])
        if chap:
            short += "·" + chap.group(1) + "章"
        units.append({"title": u["title"], "short": short, "file": u["file"], "n": len(u["cards"])})
        for ci, c in enumerate(u["cards"]):
            md = c["body"]
            md = re.sub(r"^\s*\*[^*\n]+\*\s*$", "", md, count=1, flags=re.M)
            html = markdown.markdown(fmt_html(md), extensions=["tables", "fenced_code", "sane_lists"])
            html = inline_svg(html)
            key = re.sub(r"\s+", "", html)
            cards.append({"id": c["id"], "name": c["name"], "unit": u["title"],
                          "u": ui, "i": ci, "html": html, "plain": key[:4000]})
            pos[c["id"]] = (ui, ci)

        # 单元级附录：公式总表 / 易错清单 / 关系边 / 关卡地图
        extras = u.get("extras") or []
        if extras:
            md_parts = []
            for e in extras:
                md_parts.append("## " + e["title"] + "\n\n" + e["body"])
            ah = markdown.markdown(fmt_html("\n\n".join(md_parts)),
                                   extensions=["tables", "fenced_code", "sane_lists"])
            ah = inline_svg(ah)
            cards.append({"id": short, "name": "附录：自评 · 公式 · 易错 · 关系",
                          "unit": u["title"], "u": ui, "i": 900, "html": ah,
                          "plain": re.sub(r"\s+", "", ah)[:4000], "appendix": True})
    for u in d["units"]:
        for r in u["relations"]:
            a = re.sub(r"^([A-N]-\d+(?:\.\d+)?).*", r"\1", r["from"])
            b = re.sub(r"^([A-N]-\d+(?:\.\d+)?).*", r"\1", r["to"])
            if a in pos and b in pos:
                edges.append({"a": a, "b": b, "t": r["type"]})

    guide_html = ""
    gp = ROOT / "00a-怎么用这本书.md"
    if gp.exists():
        gt = gp.read_text(encoding="utf-8")
        gt = re.sub(r"^# .*$", "", gt, count=1, flags=re.M)
        guide_html = inline_svg(markdown.markdown(gt, extensions=["tables", "fenced_code", "sane_lists"]))

    payload = json.dumps({"cards": cards, "edges": edges, "units": units,
                          "stats": d["stats"], "guide": guide_html}, ensure_ascii=False)

    tpl = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>上海高中物理知识图谱</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--ink:#1c1c1e;--sub:#6b6b70;--line:#e3e3e8;--accent:#0b6b5b;--bg:#f6f7f4}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.75 -apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;display:flex;flex-direction:column}
header{background:#fff;border-bottom:1px solid var(--line);padding:12px 20px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
header h1{font-size:17px;margin:0;color:var(--accent)}
header .stat{color:var(--sub);font-size:12.5px}
header .spacer{flex:1}
input[type=search]{border:1px solid var(--line);border-radius:8px;padding:7px 12px;font-size:14px;width:260px;outline:none}
input[type=search]:focus{border-color:var(--accent)}
.tabs{display:flex;gap:6px}
.tab{border:1px solid var(--line);background:#fff;border-radius:8px;padding:7px 14px;cursor:pointer;font-size:13.5px;color:#333}
.tab.on{background:var(--accent);color:#fff;border-color:var(--accent)}
main{flex:1;display:flex;min-height:0}
aside{width:290px;background:#fff;border-right:1px solid var(--line);overflow:auto;padding:10px 0}
aside .unit{padding:10px 16px 4px;font-size:12px;color:var(--sub);letter-spacing:.5px}
aside .item{padding:7px 16px 7px 22px;cursor:pointer;font-size:13.5px;border-left:3px solid transparent;display:flex;gap:8px}
aside .item:hover{background:#f2f7f5}
aside .item.on{background:#e9f3f0;border-left-color:var(--accent);font-weight:600}
aside .item .id{color:var(--sub);font-family:ui-monospace,Menlo,monospace;font-size:12px;min-width:44px}
#content{flex:1;overflow:auto;padding:28px 36px 80px;outline:none}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:26px 32px;max-width:860px;margin:0 auto}
.card h2{font-size:21px;color:#0a4f43;margin:0 0 4px;border-left:5px solid var(--accent);padding-left:12px}
.card h3{font-size:15.5px;color:#0a4f43;margin:24px 0 8px}
.card table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13.5px}
.card th,.card td{border:1px solid var(--line);padding:6px 9px;vertical-align:top}
.card th{background:#f0f4f2}
.card img{max-width:100%;display:block;margin:12px auto;border:1px solid #ececea;border-radius:6px}
.card img.mf{display:inline-block;margin:0 1px;vertical-align:-0.25em;border:none;border-radius:0}
.card blockquote{margin:12px 0;padding:10px 14px;background:#f1f1ec;border-left:4px solid #9a9a90;border-radius:0 6px 6px 0;font-size:13.5px;color:#444}
.card pre{background:#1f2933;color:#e6edf3;padding:12px;border-radius:8px;overflow:auto;font-size:12.5px}
.card code{background:#f0f0ea;padding:1px 4px;border-radius:4px;font-size:13px}
.card strong{color:#0a4f43}
#graph{flex:1;overflow:auto;display:none;position:relative;background:
  radial-gradient(circle at 30% 20%,#fbfdfc,#eef3f1)}
#graph>svg{width:100%;height:100%;display:block}
.node{cursor:pointer}
.node rect{transition:.15s}
.node:hover rect{filter:brightness(.96)}
.empty{color:var(--sub);text-align:center;margin-top:80px}
footer{border-top:1px solid var(--line);background:#fff;padding:6px 20px;font-size:12px;color:var(--sub);display:flex;gap:16px}
@media (max-width:820px){aside{display:none}#content{padding:16px}}
#print{display:none}
@media print{
  @page{size:A4;margin:12mm 13mm}
  header,aside,#content,#graph,footer{display:none !important}
  #print{display:block !important;padding:0}
  body{background:#fff;display:block}
  .print-card{page-break-after:auto;margin:0 0 6mm}
  .print-card h2{font-size:12pt;margin:6mm 0 2mm;padding-left:8px;border-left:4px solid #0b6b5b}
  .print-card h3{font-size:10pt;margin:4mm 0 1mm}
  .print-card p,.print-card li{font-size:9pt;line-height:1.35;margin:1mm 0}
  .print-card table{font-size:8pt;margin:2mm 0}
  .print-card th,.print-card td{padding:1.2mm 1.6mm}
  .print-card img{max-width:72%}
  .print-card h2,.print-card h3,.print-card table{break-after:avoid}
  .print-card{break-inside:auto}
  .cover{text-align:center;padding-top:70mm;page-break-after:always}
  .cover h1{font-size:26pt;color:#0b6b5b;margin:4mm 0;border:none;padding:0}
  .cover p{font-size:10pt;color:#555;margin:2mm}
  .toc{page-break-after:always}
  .toc h2{font-size:14pt;margin:0 0 4mm;color:#0b6b5b}
  .toc-item{font-size:9pt;line-height:1.55;color:#222}
  .guide{page-break-after:always}
}
</style></head>
<body>
<header>
  <h1>上海高中物理 · 知识图谱</h1>
  <span class="stat" id="stat"></span>
  <span class="spacer"></span>
  <input id="q" type="search" placeholder="搜索考点 / 公式 / 关键词…">
  <div class="tabs"><button class="tab on" data-v="card">卡片</button><button class="tab" data-v="graph">图谱</button><button class="tab" id="guideBtn">怎么用</button></div>
</header>
<main>
  <aside id="tree"></aside>
  <div id="content"><div class="card" id="card"><div class="empty">← 从左侧选一个考点</div></div></div>
  <div id="graph"><svg id="svg"><g id="edges"></g><g id="nodes"></g></svg></div>
  <div id="print"></div>
</main>
<footer><span>点击节点查看卡片</span><span>关系：前置 / 派生 / 综合 / 易错 / 实验</span><span id="fname"></span></footer>
<script>
window.MathJax = {
  tex: { inlineMath: [['\\(','\\)']], displayMath: [['\\[','\\]']] },
  svg: { fontCache: 'global', scale: 0.95 },
  startup: { typeset: false }
};
</script>
<script>__MATHJAX__</script>
<script>const DATA = __DATA__;</script>
<script>
const $ = s => document.querySelector(s);
const TYPE = __TYPE__;
let cur = null;

function buildTree(){
  const t = $('#tree'); t.innerHTML = '';
  let lastUnit = null;
  DATA.cards.forEach((c, idx) => {
    if (c.unit !== lastUnit){
      lastUnit = c.unit;
      const u = document.createElement('div');
      u.className = 'unit'; u.textContent = c.unit; t.appendChild(u);
    }
    const el = document.createElement('div');
    el.className = 'item'; el.dataset.idx = idx; el.dataset.id = c.id;
    el.innerHTML = `<span class="id">${c.id}</span><span>${c.name}</span>`;
    el.onclick = () => open(idx);
    t.appendChild(el);
  });
}
function open(idx){
  const c = DATA.cards[idx];
  cur = c.id;
  $('#card').innerHTML = `<h2>${c.id}　${c.name}</h2>` + c.html;
  if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([$('#card')]).catch(()=>{});
  $('#content').scrollTop = 0;
  document.querySelectorAll('.item').forEach(e => e.classList.toggle('on', +e.dataset.idx === idx));
  const on = document.querySelector('.item.on');
  if (on) on.scrollIntoView({block:'nearest'});
  setView('card');
}
function setView(v){
  const isCard = v === 'card';
  $('#content').style.display = isCard ? 'block' : 'none';
  $('#graph').style.display = isCard ? 'none' : 'block';
  document.querySelectorAll('.tab').forEach(b => b.classList.toggle('on', b.dataset.v === v));
  if (!isCard) drawGraph();
}
function drawGraph(){
  const svg = $('#svg');
  const W = svg.clientWidth || 900, H = svg.clientHeight || 600;
  const NS = 'http://www.w3.org/2000/svg';
  const colW = Math.max(190, W / Math.max(DATA.units.length, 1));
  const totalW = colW * Math.max(DATA.units.length, 1);
  svg.setAttribute("viewBox", `0 0 ${totalW} ${H}`);
  svg.style.width = totalW + "px";
  const edgesG = $('#edges'), nodesG = $('#nodes');
  edgesG.innerHTML = ''; nodesG.innerHTML = '';
  const COL = ['#0b6b5b','#1f6feb','#b45309','#7c3aed','#0891b2','#db2777'];
  const P = {};
  DATA.cards.forEach(c => {
    P[c.id] = {x: colW*c.u + colW/2, y: 84 + c.i * ((H-130)/Math.max(DATA.units[c.u].n,1))};
  });
  DATA.units.forEach((u,i) => {
    const t = document.createElementNS(NS,'text');
    t.setAttribute('x', colW*i + colW/2); t.setAttribute('y', 50);
    t.setAttribute('text-anchor','middle'); t.setAttribute('font-size','11.5');
    t.setAttribute('fill', COL[i % COL.length]); t.setAttribute('font-weight','600');
    t.textContent = u.short;
    nodesG.appendChild(t);
  });
  DATA.edges.forEach(e => {
    const a = P[e.a], b = P[e.b]; if (!a || !b) return;
    const same = Math.abs(a.x - b.x) < 1;
    const dx = same ? 80 : 0;
    const p = document.createElementNS(NS, 'path');
    p.setAttribute('d', 'M'+a.x+','+a.y+' C'+(a.x+dx)+','+((a.y+b.y)/2)+' '+(b.x+dx)+','+((a.y+b.y)/2)+' '+b.x+','+b.y);
    p.setAttribute('fill','none');
    p.setAttribute('stroke', TYPE[e.t] || '#c9cfcc');
    p.setAttribute('stroke-width','1.3');
    p.setAttribute('opacity','0.45');
    edgesG.appendChild(p);
  });
  DATA.cards.forEach((c, idx) => {
    if (c.appendix) return;
    const p = P[c.id], col = COL[c.u % COL.length];
    const on = c.id === cur;
    const g = document.createElementNS(NS,'g');
    g.setAttribute('class','node');
    g.setAttribute('transform', 'translate('+p.x+','+p.y+')');
    const r = document.createElementNS(NS,'rect');
    r.setAttribute('x','-75'); r.setAttribute('y','-20');
    r.setAttribute('width','150'); r.setAttribute('height','40');
    r.setAttribute('rx','9');
    r.setAttribute('fill', on ? col : '#ffffff');
    r.setAttribute('stroke', on ? col : '#d5ddda');
    const bar = document.createElementNS(NS,'rect');
    bar.setAttribute('x','-75'); bar.setAttribute('y','-20');
    bar.setAttribute('width','4.5'); bar.setAttribute('height','40');
    bar.setAttribute('fill', on ? '#ffffff' : col);
    const t1 = document.createElementNS(NS,'text');
    t1.setAttribute('x','-62'); t1.setAttribute('y','-3');
    t1.setAttribute('font-size','11.5'); t1.setAttribute('font-weight','700');
    t1.setAttribute('fill', on ? '#ffffff' : '#1c1c1e');
    t1.textContent = c.id;
    const t2 = document.createElementNS(NS,'text');
    t2.setAttribute('x','-62'); t2.setAttribute('y','12');
    t2.setAttribute('font-size','9.5');
    t2.setAttribute('fill', on ? '#d8efe9' : '#6b6b70');
    t2.textContent = c.name.length > 11 ? c.name.slice(0,11) + '…' : c.name;
    g.appendChild(r); g.appendChild(bar); g.appendChild(t1); g.appendChild(t2);
    g.onclick = () => open(idx);
    nodesG.appendChild(g);
  });
}
$('#q').addEventListener('input', e => {
  const k = e.target.value.trim().toLowerCase();
  document.querySelectorAll('.item').forEach(el => {
    const c = DATA.cards[+el.dataset.idx];
    const hit = !k || (c.id + c.name + c.plain).toLowerCase().includes(k);
    el.style.display = hit ? '' : 'none';
  });
});
document.querySelectorAll('.tab[data-v]').forEach(b => b.onclick = () => { setView(b.dataset.v); history.replaceState(null,'',b.dataset.v==='graph'?'#graph':'#card'); });
$('#guideBtn').onclick = () => {
  $('#card').innerHTML = DATA.guide;
  $('#content').style.display = 'block'; $('#graph').style.display = 'none';
  document.querySelectorAll('.item').forEach(e => e.classList.remove('on'));
  document.querySelectorAll('.tab[data-v]').forEach(b => b.classList.remove('on'));
};
document.addEventListener('keydown', e => {
  if (e.key === '/' ) { e.preventDefault(); $('#q').focus(); }
});
buildTree();
// 打印版：把所有卡片顺序铺开，供 Chrome 直接打印成 PDF
(function(){
  const box = $('#print');
  const cover = `<section class="cover">
      <h1>上海高中物理</h1><h1>知 识 图 谱</h1>
      <p>上海高中物理 · 六册 · 166 考点 · 498 例题</p>
      <p>2026-10-30</p></section>`;
  const toc = '<section class="toc"><h2>目　录</h2>' +
    DATA.cards.map(c => `<div class="toc-item">${c.id}　${c.name}</div>`).join('') +
    '</section>';
  const guide = `<section class="guide">${DATA.guide || ''}</section>`;
  box.innerHTML = cover + toc + guide + DATA.cards.map(c =>
    `<article class="print-card"><h2>${c.id}　${c.name}</h2>${c.html}</article>`
  ).join('');
})();
// 支持 #c=考点编号 深链，例如 #c=C-8
(function(){
  const m = location.hash.match(/^#c=(.+)$/);
  if (m) {
    const i = DATA.cards.findIndex(c => c.id === decodeURIComponent(m[1]));
    if (i >= 0) { open(i); return; }
  }
  document.querySelectorAll('.item')[0].click();
if (window.MathJax && MathJax.typesetPromise) {
  MathJax.typesetPromise([document.getElementById('print')]).then(()=>{window.__MJ_DONE__=true;}).catch(()=>{window.__MJ_DONE__=true;});
}
})();
$('#stat').textContent = `${DATA.stats.units} 单元 · ${DATA.stats.cards} 考点 · ${DATA.stats.examples} 例题 · ${DATA.stats.formulas} 公式`;
$('#fname').textContent = DATA.cards.length + ' 个考点';
if (location.hash === '#graph') setView('graph');
</script>
</body></html>"""

    mj = (ROOT / "build" / "assets" / "mathjax-tex-svg.js")
    mj_src = mj.read_text(encoding="utf-8") if mj.exists() else ""
    html = (tpl.replace("__DATA__", payload)
               .replace("__TYPE__", json.dumps(TYPE_COLOR, ensure_ascii=False))
               .replace("__MATHJAX__", mj_src))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print("saved", OUT, round(OUT.stat().st_size / 1024), "KB",
          "| cards", len(cards), "| edges", len(edges))


if __name__ == "__main__":
    main()
