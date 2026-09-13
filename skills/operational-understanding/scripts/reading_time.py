#!/usr/bin/env python3
"""Estimate reading time per section of an operational-understanding HTML artifact.

Prose 220 wpm, code 90 wpm, +30 s per diagram, +20 s per table. Sections are split on
<h2>/<h3>. Prints one line per section plus per-level and total; exits 1 if any section
exceeds --limit minutes so it can gate publishing.
"""
import argparse
import html
import re
import sys

PROSE_WPM = 220
CODE_WPM = 90
DIAGRAM_S = 30
TABLE_S = 20


def strip_tags(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", s))


def estimate(block: str) -> float:
    code = re.findall(r"<pre[^>]*>(.*?)</pre>", block, re.S)
    code_words = sum(len(strip_tags(c).split()) for c in code)
    diagrams = len(re.findall(r'<figure class="diagset"', block)) + len(re.findall(r"<svg\b", block))
    tables = len(re.findall(r"<table\b", block))
    prose_only = re.sub(r"<pre.*?</pre>", " ", block, flags=re.S)
    prose_only = re.sub(r"<svg.*?</svg>", " ", prose_only, flags=re.S)
    prose_words = len(strip_tags(prose_only).split())
    seconds = (
        prose_words / PROSE_WPM * 60
        + code_words / CODE_WPM * 60
        + diagrams * DIAGRAM_S
        + tables * TABLE_S
    )
    return seconds / 60


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--limit", type=float, default=5.0, help="max minutes per section")
    args = ap.parse_args()
    text = open(args.path, encoding="utf-8").read()

    # Drill-down layout: one card per <article data-level data-title>. Fall back to <h2>/<h3>
    # splitting for the single-page layout.
    text = re.sub(r"<(style|script)\b.*?</\1>", " ", text, flags=re.S)
    if re.search(r"<article[^>]*data-title=", text):
        parts = re.split(r'(?=<article\b|<section[^>]*data-route="/(?:map|why)")', text)
    else:
        parts = re.split(r"(?=<h[23]\b)", text)
    over = False
    level_totals: dict[str, float] = {}
    current_level = "front-matter"
    grand = 0.0
    for part in parts:
        card = re.match(r'<article[^>]*data-level="([^"]+)"[^>]*data-title="([^"]*)"', part)
        m = re.match(r"<h([23])[^>]*>(.*?)</h\1>", part, re.S)
        if card:
            current_level = card.group(1)
            title = html.unescape(card.group(2))
        elif part.startswith("<section") and 'data-route="/map"' in part:
            current_level = title = "map"
        elif part.startswith("<section") and 'data-route="/why"' in part:
            current_level = title = "principles"
        else:
            title = strip_tags(m.group(2)).strip() if m else "(front matter)"
            if m and m.group(1) == "2":
                current_level = title
        mins = estimate(part)
        grand += mins
        level_totals[current_level] = level_totals.get(current_level, 0.0) + mins
        flag = "  <-- OVER" if mins > args.limit else ""
        over |= bool(flag)
        print(f"{mins:5.1f} min  {title}{flag}")
    print("-" * 60)
    for lvl, mins in level_totals.items():
        print(f"{mins:5.1f} min  [level] {lvl}")
    print(f"{grand:5.1f} min  TOTAL")
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
