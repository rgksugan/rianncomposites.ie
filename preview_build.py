#!/usr/bin/env python3
"""Minimal Jekyll-like renderer for LOCAL PREVIEW ONLY.
Handles the small Liquid subset used by this site so we can eyeball the design
without a full Ruby/Jekyll toolchain. GitHub Pages still does the real build.
"""
import os, re, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "_preview")

SITE = {
    "title": "Riann Composites",
    "tagline": "Fiberglass & Carbon Fiber Repair Specialist",
    "description": "Riann Composites are fiberglass and carbon fiber repair specialists based in Tulla, Co. Clare, Ireland. We repair campers, boats, cars, carbon fiber parts and industrial structures — saving you thousands compared to replacement. We repair it, we don't replace it.",
    "formspree_id": "your-form-id",
    "business": {
        "phone_display": "+353 87 123 4567",
        "phone_link": "+353871234567",
        "whatsapp": "353871234567",
        "email": "info@rianncomposites.ie",
        "address": "Tulla, Co. Clare, Ireland",
        "area": "Serving customers across Ireland",
    },
}
BASEURL = ""  # local preview served at root


def parse_front_matter(text):
    fm = {}
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        block = text[3:end].strip("\n")
        body = text[end + 4:]
        lines = block.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            m = re.match(r"^(\w+):\s*(.*)$", line)
            if m:
                key, val = m.group(1), m.group(2).strip()
                if val in (">-", ">", "|", "|-"):  # block scalar
                    collected = []
                    i += 1
                    while i < len(lines) and (lines[i].startswith("  ") or lines[i].strip() == ""):
                        collected.append(lines[i].strip())
                        i += 1
                    fm[key] = " ".join(c for c in collected if c)
                    continue
                if val == "null" or val == "":
                    fm[key] = None
                else:
                    fm[key] = val.strip('"').strip("'")
            i += 1
    return fm, body


def resolve_var(path, page):
    cur = {"page": page, "site": SITE}
    parts = path.split(".")
    val = cur.get(parts[0])
    for p in parts[1:]:
        if isinstance(val, dict):
            val = val.get(p)
        else:
            return None
    return val


def apply_filters(value, filters, page):
    for f in filters:
        f = f.strip()
        if f.startswith("default:"):
            if value in (None, ""):
                arg = f[len("default:"):].strip()
                value = resolve_expr_token(arg, page)
        elif f == "strip_newlines":
            if isinstance(value, str):
                value = value.replace("\n", " ").strip()
        elif f == "relative_url":
            value = BASEURL + (value or "")
        elif f == "absolute_url":
            value = BASEURL + (value or "")
        elif f.startswith("date:"):
            value = "2026"
    return value


def resolve_expr_token(tok, page):
    tok = tok.strip()
    if (tok.startswith("'") and tok.endswith("'")) or (tok.startswith('"') and tok.endswith('"')):
        return tok[1:-1]
    if tok == "now":
        return "now"
    v = resolve_var(tok, page)
    return v


def render_expr(expr, page):
    segs = expr.split("|")
    base = segs[0].strip()
    val = resolve_expr_token(base, page)
    val = apply_filters(val, segs[1:], page)
    return "" if val is None else str(val)


def render_liquid(text, page, content=None):
    # includes
    def inc(m):
        name = m.group(1).strip()
        with open(os.path.join(ROOT, "_includes", name), encoding="utf-8") as fh:
            return render_liquid(fh.read(), page, content)
    text = re.sub(r"\{%\s*include\s+([^\s%]+)\s*%\}", inc, text)

    # if / else / endif  (single level, condition = truthiness of one var)
    def ifblock(m):
        cond = m.group(1).strip()
        truthy = m.group(2)
        falsy = m.group(3) or ""
        val = resolve_expr_token(cond, page)
        return truthy if val else falsy
    text = re.sub(
        r"\{%\s*if\s+([^%]+?)\s*%\}(.*?)(?:\{%\s*else\s*%\}(.*?))?\{%\s*endif\s*%\}",
        ifblock, text, flags=re.S)

    # content
    if content is not None:
        text = text.replace("{{ content }}", content)

    # expressions
    text = re.sub(r"\{\{\s*(.*?)\s*\}\}", lambda m: render_expr(m.group(1), page), text)
    return text


def build_page(src, out_rel):
    with open(os.path.join(ROOT, src), encoding="utf-8") as fh:
        raw = fh.read()
    fm, body = parse_front_matter(raw)
    page = dict(fm)
    page.setdefault("title", None)
    page["url"] = "/" + out_rel.replace("index.html", "")
    rendered_body = render_liquid(body, page)
    layout = fm.get("layout", "default")
    with open(os.path.join(ROOT, "_layouts", layout + ".html"), encoding="utf-8") as fh:
        layout_html = fh.read()
    full = render_liquid(layout_html, page, content=rendered_body)
    dest = os.path.join(OUT, out_rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(full)
    print("built", out_rel)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    # copy assets
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))
    build_page("index.html", "index.html")
    build_page("contact.html", "contact/index.html")
    build_page("404.html", "404.html")


if __name__ == "__main__":
    main()
