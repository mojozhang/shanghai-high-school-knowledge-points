#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""纯文本公式 → LaTeX（MathJax 可渲染），统一处理 Unicode 上下标、希腊字母、组合重音。

设计原则：
1. 源文件写"人看着舒服"的形式（v₀、x²、√(2h/g)、v̄）；
2. 转换器负责映射成标准 LaTeX，不留任何非 ASCII 字符；
3. 映射不到的字符一律降级为原样文本，绝不输出半截公式。
"""
import hashlib
import pathlib
import re

try:                     # 渲染时才需要，未安装则走"只读缓存"模式
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: E402
    _HAS_MPL = True
except Exception:        # pragma: no cover
    plt = None
    _HAS_MPL = False

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "图" / "公式"

# ---------- 字符映射表 ----------
GREEK = {
    "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta",
    "ε": r"\varepsilon", "ζ": r"\zeta", "η": r"\eta", "θ": r"\theta",
    "ι": r"\iota", "κ": r"\kappa", "λ": r"\lambda", "μ": r"\mu",
    "ν": r"\nu", "ξ": r"\xi", "ο": "o", "π": r"\pi", "ρ": r"\rho",
    "σ": r"\sigma", "τ": r"\tau", "υ": r"\upsilon", "φ": r"\varphi",
    "χ": r"\chi", "ψ": r"\psi", "ω": r"\omega",
    "Γ": r"\Gamma", "Δ": r"\Delta", "Θ": r"\Theta", "Λ": r"\Lambda",
    "Ξ": r"\Xi", "Π": r"\Pi", "Σ": r"\Sigma", "Υ": r"\Upsilon",
    "Φ": r"\Phi", "Ψ": r"\Psi", "Ω": r"\Omega",
}

SYMBOLS = {
    "×": r"\times", "÷": r"\div", "·": r"\cdot", "−": "-", "–": "-",
    "≈": r"\approx", "≠": r"\neq", "≤": r"\leq", "≥": r"\geq",
    "→": r"\to", "⇒": r"\Rightarrow", "⇔": r"\Leftrightarrow",
    "∝": r"\propto", "∞": r"\infty", "±": r"\pm", "∓": r"\mp",
    "∠": r"\angle", "⊥": r"\perp", "∥": r"\parallel", "△": r"\triangle",
    "°": r"^{\circ}", "℃": r"^{\circ}\mathrm{C}", "%": r"\%",
    "′": "'", "″": "''",
    "∑": r"\sum", "∫": r"\int", "∂": r"\partial",
    "≪": r"\ll", "≫": r"\gg", "⇄": r"\rightleftharpoons",
    "⇌": r"\rightleftharpoons", "≡": r"\equiv", "∛": r"\sqrt[3]", "∜": r"\sqrt[4]",
}

SUP = {
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
    "⁺": "+", "⁻": "-", "ⁿ": "n", "ⁱ": "i",
    "²": "2", "³": "3", "¹": "1",       # U+00B2/B3/B9
}
SUB = {
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
    "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
    "₊": "+", "₋": "-", "ₐ": "a", "ₑ": "e", "ₒ": "o",
    "ₓ": "x", "ₙ": "n", "ₖ": "k", "ₘ": "m", "ₚ": "p",
}

BASE = r"A-Za-z0-9\)\]\{\}α-ωΑ-Ω"
SUB_CHARS = "".join(SUB)
SUP_CHARS = "".join(SUP)


def _readable(s: str) -> bool:
    """是否只含可转换字符（不含中文等）。"""
    for c in s:
        if ord(c) < 128 or c in " \t":
            continue
        if c in GREEK or c in SYMBOLS or c in SUB or c in SUP:
            continue
        if 0x0300 <= ord(c) <= 0x036F:
            continue
        return False
    return True


def to_latex(s: str) -> str:
    s = s.strip()

    # 1. 组合重音：v̄ → \bar{v}
    s = re.sub(r"([A-Za-zα-ωΑ-Ω])\u0304", lambda m: r"\bar{" + m.group(1) + "}", s)
    s = re.sub(r"([A-Za-zα-ωΑ-Ω])\u0305", lambda m: r"\overline{" + m.group(1) + "}", s)
    s = re.sub(r"([A-Za-zα-ωΑ-Ω])\u0307", lambda m: r"\dot{" + m.group(1) + "}", s)
    s = re.sub(r"([A-Za-zα-ωΑ-Ω])\u0308", lambda m: r"\ddot{" + m.group(1) + "}", s)

    # 2. 常用分数
    s = s.replace("½", r"\frac{1}{2}").replace("¼", r"\frac{1}{4}").replace("¾", r"\frac{3}{4}")

    # 3. 根号
    RAD = {"√": "", "∛": "[3]", "∜": "[4]"}
    out, i = [], 0
    while i < len(s):
        if s[i] in RAD:
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
                out.append(r"\sqrt" + RAD[s[i]] + "{" + to_latex(s[j + 1:k]) + "}")
                i = k + 1
                continue
            m2 = re.match(r"[A-Za-z0-9.]+|[" + "".join(GREEK) + r"]", s[j:])
            arg = m2.group(0) if m2 else ""
            out.append(r"\sqrt" + RAD[s[i]] + "{" + arg + "}")
            i = j + len(arg) if arg else j
            continue
        out.append(s[i])
        i += 1
    s = "".join(out)

    # 4. 下标（含下划线写法与 Unicode 下标）
    KNOWN = {"max", "min", "avg", "tot", "net", "eq", "cm", "ab", "bc", "ac", "cd"}

    def _sub(m):
        base, word = m.group(1), m.group(2)
        w = word if word in KNOWN else word[0]
        return base + "_{" + w + "}" + word[len(w):]

    s = re.sub(r"([" + BASE + r"])_([A-Za-z0-9]+)", _sub, s)
    s = re.sub(r"([" + BASE + r"])([" + SUB_CHARS + r"]+)",
               lambda m: m.group(1) + "_{" + "".join(SUB[c] for c in m.group(2)) + "}", s)

    # 5. 上标
    s = re.sub(r"([" + BASE + r"])([" + SUP_CHARS + r"]+)",
               lambda m: m.group(1) + "^{" + "".join(SUP[c] for c in m.group(2)) + "}", s)

    # 6. 希腊字母与符号
    for k in sorted(GREEK, key=len, reverse=True):
        s = s.replace(k, GREEK[k] + " ")
    for k in sorted(SYMBOLS, key=len, reverse=True):
        s = s.replace(k, SYMBOLS[k] + " ")

    # 7. 函数名正体
    for fn in ["sin", "cos", "tan", "cot", "sec", "csc", "max", "min", "ln", "lg", "log"]:
        s = re.sub(r"(?<![\\A-Za-z])" + fn + r"\b", lambda m: r"\mathrm{" + m.group(0) + "}", s)

    s = re.sub(r"\s+", " ", s).strip()
    # 兜底：仍残留的上下标字符（前面没有基底）→ 空基底上标
    for c, v in SUP.items():
        s = s.replace(c, "{}^" + v)
    for c, v in SUB.items():
        s = s.replace(c, "{}_" + v)

    # 片段被截断时可能以 ^ 或 _ 开头（无基底），补一个空基底
    if s.startswith("^") or s.startswith("_"):
        s = "{}" + s
    return s


def is_formula(s: str) -> bool:
    s = s.strip()
    if not s or len(s) > 60:
        return False
    if not _readable(s):
        return False
    if not re.search(r"[A-Za-z" + "".join(GREEK) + r"]", s):
        return False
    if not re.search(r"[=≈∝≤≥√+\-−×÷/]", s):
        return False
    return True


def needs_render(s: str) -> bool:
    """含根号/上下标/分数/组合重音/下划线的公式值得单独渲染。"""
    return any(c in s for c in "√²³⁰¹⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉_^½")


SPAN_RE = re.compile(
    r"[A-Za-z0-9₀-₉⁰-⁹²³α-ωΑ-Ω√∝=+\-−×÷/()\[\].,·_{} \t"
    r"≤≥≈≠<>→⇒%°′≪≫⇄∛∜\u0300-\u036f]{2,}")


def spans(text: str, whole: bool = False):
    """在中文句子中找出可渲染的公式片段，返回 [(start, end, formula)]。"""
    out = []
    for m in SPAN_RE.finditer(text):
        raw = m.group(0)
        if not any(k in raw for k in "=√∝≪≫≈"):
            continue
        if not re.search(r"[A-Za-z" + "".join(GREEK) + r"]", raw):
            continue
        if not whole and not needs_render(raw):
            continue
        a, b = m.start(), m.end()
        while a < b and text[a] in " \t":
            a += 1
        while b > a and text[b - 1] in " \t":
            b -= 1
        raw = text[a:b]
        lead = len(raw) - len(raw.lstrip(" \t-−·,;:"))
        trail = len(raw) - len(raw.rstrip(" \t-−·,;:"))
        a, b = a + lead, b - trail
        frag = text[a:b]
        if not frag or any(ch in frag for ch in "，。\n"):
            continue
        if not _readable(frag):
            continue
        if frag[-1] in "_^=+−-/\\":
            continue          # 截断在运算符上的片段不可用
        out.append((a, b, frag))
    return out


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
    for t in ["v̄ = Δx/Δt", "v̄ = (v₀ + v)/2", "v² − v₀² = 2ax",
              "Φ = BS", "ΣF = ma", "ν = c/λ", "θ = 30°"]:
        print(f"{t:22s} → {to_latex(t)}")
