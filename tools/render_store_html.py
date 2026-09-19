"""Render the store descriptions to HTML for the CurseForge Author Console's editor (headings, paragraphs, bold,
links, inline code, lists, tables; lines that already are HTML pass through untouched):

    docs/public/store-description.md -> .html   (the modpack)
    docs/core/store-description.md   -> .html   (Ninjacat Skies Core)

    python tools/render_store_html.py

The "CurseForge summary (one line)" paragraph stays in the HTML for the author; tools/cf_update_pages.py strips it
before publishing.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "docs/public/store-description.md", ROOT / "docs/core/store-description.md"]


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"``\s?(.+?)\s?``", r"<code>\1</code>", text)
    text = re.sub(r"(?<![<\w])`([^`<]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def render(md: str) -> str:
    out, lines, i = [], md.splitlines(), 0
    para: list[str] = []

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        if line.startswith("<"):
            flush()
            out.append(line)
        elif line.startswith("# "):
            flush()
            out.append("<p><strong>" + inline(line[2:]) + "</strong></p>")
        elif line.startswith("## "):
            flush()
            out.append("\n<h2>" + inline(line[3:]) + "</h2>")
        elif line.startswith("- "):
            flush()
            out.append("<ul>")
            while i < len(lines) and lines[i].startswith("- "):
                out.append("<li>" + inline(lines[i][2:]) + "</li>")
                i += 1
            out.append("</ul>")
            continue
        elif re.match(r"^\d+\. ", line):
            flush()
            out.append("<ol>")
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                out.append("<li>" + inline(re.sub(r"^\d+\. ", "", lines[i])) + "</li>")
                i += 1
            out.append("</ol>")
            continue
        elif line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                if not all(re.fullmatch(r"-*", c) for c in cells):
                    rows.append(cells)
                i += 1
            out.append("<table>")
            for cells in rows:
                if any(cells):
                    out.append("<tr>" + "".join("<td>" + inline(c) + "</td>" for c in cells) + "</tr>")
            out.append("</table>")
            continue
        elif line.startswith("!["):
            flush()
            m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line)
            if m:
                out.append(f'<p><img src="{m.group(2)}" alt="{html.escape(m.group(1))}"></p>')
        elif line.strip() == "":
            flush()
        else:
            para.append(line.strip())
        i += 1
    flush()
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    for src in PAGES:
        out = src.with_suffix(".html")
        out.write_text(render(src.read_text(encoding="utf-8")), encoding="utf-8")
        print("wrote", out)
