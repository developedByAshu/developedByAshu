"""Sets text as vector outlines from glyphs.json, so the profile looks the same on any device. Standard library only."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

FONTS = json.loads((Path(__file__).resolve().parent / "glyphs.json").read_text(encoding="utf-8"))


def width(text, weight, size, tracking=0.0):
    """Returns the set width of the text in pixels."""
    font = FONTS[weight]
    units = sum(font["glyphs"][char][0] for char in text) + sum(font["kern"].get(pair, 0) for pair in map("".join, zip(text, text[1:])))
    return units * size / font["upm"] + tracking * max(len(text) - 1, 0)


def wrap(text, weight, size, limit):
    """Breaks text into lines no wider than the limit."""
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if width(trial, weight, size) > limit and current:
            lines.append(current)
            current = word
        else:
            current = trial
    return lines + [current]


class Sheet:
    """Collects shapes and outlined text, and writes one SVG."""

    def __init__(self, page_width, title):
        self.width, self.title, self.parts, self.defs, self.used = page_width, title, [], [], set()

    def raw(self, markup):
        self.parts.append(markup)

    def text(self, x, y, text, size, fill, weight="regular", tracking=0.0, anchor="start"):
        font = FONTS[weight]
        scale = size / font["upm"]
        if anchor == "end":
            x -= width(text, weight, size, tracking)
        uses, cursor = [], 0.0
        for index, char in enumerate(text):
            if char != " ":
                self.used.add((weight, char))
                uses.append(f'<use href="#{weight[:2]}{ord(char)}" x="{cursor:.0f}"/>')
            cursor += font["glyphs"][char][0] + font["kern"].get(text[index:index + 2], 0) + tracking / scale
        self.parts.append(f'<g fill="{fill}" transform="translate({x:.2f} {y:.2f}) scale({scale:.5f} {-scale:.5f})">{"".join(uses)}</g>')

    def save(self, path, height):
        glyphs = "".join(f'<path id="{weight[:2]}{ord(char)}" d="{FONTS[weight]["glyphs"][char][1]}"/>' for weight, char in sorted(self.used))
        height = round(height)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {height}" role="img" aria-label="{escape(self.title)}"><defs>{"".join(self.defs)}{glyphs}</defs>{"".join(self.parts)}</svg>'
        Path(path).write_text(svg.replace("%HEIGHT%", str(height)).replace("%INNER%", str(height - 1)), encoding="utf-8", newline="\n")
