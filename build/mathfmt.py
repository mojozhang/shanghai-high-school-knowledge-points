#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把纯文本公式转成 LaTeX（mathtext 子集）并渲染成透明 PNG。

设计取舍：
- PDF(Word) 与 HTML 共用同一批 PNG，保证两处长相一致；
- 只渲染"展示型公式"（表格里的公式单元格、要点里的公式），行内仍用正体+上下标，
  避免行内小图基线跳动。
"""
import hashlib
import pathlib
import re

try:                     # 渲染时再导入，未安装时走"只读缓存"模式
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: E402
    _HAS_MPL = True
except Exception:        # pragma: no cover
    plt = None
    _HAS_MPL = False

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "图" / "公式"

GREEK = {
    "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta",
    "θ": r"\theta", "λ": r"\lambda", "μ": r"\mu", "ρ": r"\rho",
    "ε": r"\varepsilon", "φ": r"\varphi", "ω": r"\omega", "η": r"\eta",
    "σ": r"\sigma", "τ": r"\tau", "π": r"\pi", "Δ": r"\Delta",
    "Ω": r"\Omega", "∝": r"\propto", "≈": r"\approx", "≠": r"\neq",
    "≤": r"\le", "≥": r"\ge", "→": r"\to", "⇒": r"\Rightarrow", "⇔": r"\Leftrightarrow", "×": r"\times",
    "÷": r"\div", "·": r"\cdot", "−": "-", "∞": r"\infty",
    "√": r"\sqrt", "℃": r"^{\circ}\mathrm{C}", "°": r"^{\circ}",
}
SUB = "₀₁₂₃₄₅₆₇₈₉"
SUB_MAP = {c: str(i) for i, c in enumerate(SUB)}
SUP_MAP = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
           "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-"}

# 只把这些字符集内的字符串视为"公式"
FORMULA_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    "0123456789+-−*/×÷·=≈≠≤≥<>^_()[]{}.,;:′%°√∝→∞"
                    " \t" + "".join(GREEK) + "".join(SUB) + "".join(SUP_MAP))


def needs_render(s: str) -> bool:
    """只有含根号/上下标/分数/下划线写法的才值得渲染成图片。"""
    return any(c in s for c in "√²³⁰¹⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉_^½")


SPAN_RE = re.compile(r"[A-Za-z0-9₀-₉⁰-⁹²³α-ωΑ-Ω√∝=+\-−×÷/()\[\].,·_{} \t≤≥≈≠<>→⇒%°′]{2,}")


def spans(text: str, whole: bool = False):
    """在中文句子中找出可渲染的公式片段，返回 [(start, end, formula)]。"""
    out = []
    for m in SPAN_RE.finditer(text):
        raw = m.group(0)
        if "=" not in raw and "√" not in raw and "∝" not in raw:
            continue
        if not re.search(r"[A-Za-z" + "".join(GREEK) + r"]", raw):
            continue
        if not whole and not needs_render(raw):
            continue
        a, b = m.start(), m.end()
        while a < b and text[a] == " ":
            a += 1
        while b > a and text[b - 1] == " ":
            b -= 1
        frag = text[a:b]
        frag = frag.strip(" \t-−·,;:")
        b = a + len(frag)
        if not frag or any(ch in frag for ch in "，。\n"):
            continue
        out.append((a, b, frag))
    return out


def is_formula(s: str) -> bool:
    s = s.strip()
    if not s or len(s) > 60:
        return False
    if any(ch not in FORMULA_CHARS for ch in s):
        return False
    # 至少含一个运算符或根号，且含字母，避免把普通数字/单词当公式
    if not re.search(r"[A-Za-z" + "".join(GREEK) + r"]", s):
        return False
    if not re.search(r"[=≈∝≤≥√+\-−×÷/]", s):
        return False
    return True


def to_latex(s: str) -> str:
    s = s.strip()
    s = s.replace("½", r"\frac{1}{2}").replace("¼", r"\frac{1}{4}")
    # √( ... ) -> \sqrt{ ... }
    out, i = [], 0
    while i < len(s):
        if s[i] == "√":
            j = i + 1
            if j < len(s) and s[j] == "(":
                depth, k = 0, j
                while k < len(s):
                    if s[k] == "(":
                        depth += 1
                    elif s[k] == ")":
                        depth -= 1
                        if depth == 0:
                            break
                    k += 1
                out.append(r"\sqrt{" + to_latex(s[j + 1:k]) + "}")
                i = k + 1
                continue
            m2 = re.match(r"[A-Za-z0-9.]+", s[j:])
            arg = m2.group(0) if m2 else (s[j] if j < len(s) else "")
            out.append(r"\sqrt{" + arg + "}")
            i = j + len(arg)
            continue
        out.append(s[i])
        i += 1
    s = "".join(out)

    # 下划线写法：v_H2 / v_max -> v_{H2} / v_{max}
    s = re.sub(r"([A-Za-z])_([A-Za-z0-9₀₁₂₃₄₅₆₇₈₉]+)", r"\1_{\2}", s)

    # 下标：字母/右括号 + 连续下标字符
    def sub_repl(m):
        return m.group(1) + "_{" + "".join(SUB_MAP[c] for c in m.group(2)) + "}"
    s = re.sub(r"([A-Za-z\)])([" + SUB + r"]+)", sub_repl, s)

    # 上标
    def sup_repl(m):
        return m.group(1) + "^{" + "".join(SUP_MAP[c] for c in m.group(2)) + "}"
    s = re.sub(r"([A-Za-z0-9\)])([" + "".join(SUP_MAP) + r"]+)", sup_repl, s)

    # 希腊字母与符号（按长度降序，避免 ℃ 被拆成 °）
    for k in sorted(GREEK, key=len, reverse=True):
        s = s.replace(k, GREEK[k] + " ")
    # 函数名用正体
    for fn in ["sin", "cos", "tan", "max", "min", "ln", "log"]:
        s = re.sub(r"\b" + fn + r"\b", r"\\mathrm{" + fn + "}", s)

    # 百分号转义
    s = s.replace("%", r"\%")
    return s.strip()


def render(formula: str, fontsize: float = 13.0):
    """返回 (png_path, width_cm, height_cm)；失败返回 None。"""
    if "\n" in formula or "$" in formula:
        return None
    latex = to_latex(formula)
    key = hashlib.md5((latex + "|" + str(fontsize)).encode()).hexdigest()[:16]
    CACHE.mkdir(parents=True, exist_ok=True)
    png = CACHE / f"{key}.png"
    if png.exists():
        from PIL import Image
        w, h = Image.open(png).size
        return png, w / 400 * 2.54, h / 400 * 2.54
    if not _HAS_MPL:
        return None
    try:
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.text(0, 0, f"${latex}$", fontsize=fontsize, color="black")
        fig.savefig(png, dpi=400, transparent=True,
                    bbox_inches="tight", pad_inches=0.02)
        plt.close(fig)
    except Exception:
        try:
            plt.close(fig)
        except Exception:
            pass
        return None
    from PIL import Image
    w, h = Image.open(png).size
    return png, w / 400 * 2.54, h / 400 * 2.54


if __name__ == "__main__":
    tests = ["v = v₀ + at", "x = v₀t + ½at²", "F = kx", "W = Flcosα",
             "v = √(2h/g)", "E = mc²", "R = R₁R₂/(R₁+R₂)", "B = F/(IL)"]
    for t in tests:
        r = render(t)
        print(t, "->", "OK" if r else "FAIL", round(r[1], 2) if r else "")
