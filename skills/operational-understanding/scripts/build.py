#!/usr/bin/env python3
"""Build an operational-understanding artifact from a content spec.

    build.py spec.json out.html            # build, lint, run diagram + reading-time checks
    build.py spec.json out.html --no-node  # skip the node-based diagram layout check

The model writes the SPEC (data); this script writes the HTML. Everything that has ever gone
wrong by hand is assigned or checked here: part numbers, chip colors and labels come from one
list; diagram node labels come from the same list; the shell (CSS, router, diagram engine,
lightbox) comes from templates/drilldown.html; and the output is refused if a lint rule or a
layout check fails.

Spec shape (see reference/spec-schema.md for the full description):

{
  "title": "Subsystem Name", "favicon": "🔌",
  "branch": "branch @ sha", "focus": "path/to/module (Class, Class)",
  "container": {"id": "loop", "name": "The Loop"},                  # unnumbered frame; optional
  "parts": [{"id": "connect", "name": "Connecting & disconnecting"}, ...],   # numbered in this order
  "plain": ["<p>…</p>", ...],
  "vocabulary": "<b>main</b> = …",
  "high": [card, card],  "mid": [card per part],  "low": [card per part],
  "traces": [card, ...], "principles": [{"name","why","where"}], "map": [{"symptom","part","open","grep"}],
  "tab_intros": {"high": "…", "mid": "…", "low": "…", "traces": "…"}
}
card = {"route": "slug", "part": "connect" (mid/low only), "title": "…", "fn": "…", "hook": "…",
        "body": "<html fragment with tokens>", "diagrams": [diagram spec, ...]}

Tokens inside any text: {{part:ID}} → numbered chip with name · {{n:ID}} → number-only chip ·
{{L}} → container chip · {{name:ID}} → plain "N Name" text. Diagram specs reference parts as
"part": "ID" on nodes/cols; the builder fills the label and color.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "templates", "drilldown.html")
PART_CLASS = ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]


class Lint:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")


def load_shell():
    t = open(TEMPLATE, encoding="utf-8").read()
    style = re.search(r"<style>.*?</style>", t, re.S).group(0)
    script = t[t.rindex("<script>"): t.rindex("</script>") + 9]
    return style, script


# ---------------------------------------------------------------- tokens

def make_token_renderer(spec, lint):
    parts = spec["parts"]
    num = {p["id"]: i + 1 for i, p in enumerate(parts)}
    name = {p["id"]: p["name"] for p in parts}
    cls = {p["id"]: PART_CLASS[i] for i, p in enumerate(parts)}
    cont = spec.get("container")

    def chip(pid, number_only=False):
        if pid == "L":
            return f'<span class="part pL">{esc(cont["name"])}</span>' if cont else ""
        return f'<span class="part {cls[pid]}">{num[pid]}{"" if number_only else " " + esc(name[pid])}</span>'

    def render(text, where):
        def sub(m):
            kind, pid = m.group(1), m.group(2)
            if kind == "L":
                if not cont:
                    lint.err(where, "{{L}} used but spec has no container")
                    return ""
                return chip("L")
            if pid is None or pid not in num:
                lint.err(where, f"unknown part id in token {m.group(0)}")
                return m.group(0)
            if kind == "part":
                return chip(pid)
            if kind == "n":
                return chip(pid, True)
            return f"{num[pid]} {esc(name[pid])}"  # name
        return re.sub(r"\{\{(L|part|n|name)(?::([A-Za-z0-9_-]+))?\}\}", sub, text)

    return render, num, name, cls


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- diagrams

def resolve_diagram(d, num, name, lint, where, cont=None):
    """Fill labels/colors from the parts list; validate ids."""
    d = json.loads(json.dumps(d))
    if d.get("type") == "seq":
        ids = set()
        for c in d["cols"]:
            ids.add(c["id"])
            if c.pop("black", False):
                c["faded"] = True
            if "part" in c:
                pid = c["part"]
                if pid == "L" or (cont and pid == cont["id"]):
                    c["part"] = "L"
                elif pid in num:
                    c.setdefault("label", f"{num[pid]} {name[pid]}")
                    c["part"] = num[pid]
                else:
                    lint.err(where, f"seq col references unknown part '{pid}'")
            if not c.get("label"):
                lint.err(where, f"seq col '{c['id']}' has no label")
        for st in d["steps"]:
            for k in ("from", "to"):
                if st[k] not in ids:
                    lint.err(where, f"seq step {k}='{st[k]}' is not a column id")
    else:
        ids = set()
        for n in d["nodes"]:
            ids.add(n["id"])
            if n.pop("black", False):
                n["faded"] = True
            if "part" in n:
                pid = n["part"]
                if pid == "L" or (cont and pid == cont["id"]):
                    n["part"] = "L"
                elif pid in num:
                    n.setdefault("label", f"{num[pid]} {name[pid]}")
                    n["part"] = num[pid]
                else:
                    lint.err(where, f"arch node references unknown part '{pid}'")
            if not n.get("label"):
                lint.err(where, f"arch node '{n['id']}' has no label")
            if n["col"] >= len(d["cols"]):
                lint.err(where, f"node {n['id']} col {n['col']} out of range")
            if n["row"] >= d["rows"]:
                lint.err(where, f"node {n['id']} row {n['row']} out of range")
        for e in d["edges"]:
            for k in ("from", "to"):
                if e[k] not in ids:
                    lint.err(where, f"arch edge {k}='{e[k]}' is not a node id")
        for f in d.get("frames", []):
            if f["rowTo"] < f["rowFrom"]:
                lint.err(where, "frame rowTo < rowFrom")
    if not d.get("caption"):
        lint.warn(where, f"diagram '{d.get('title')}' has no caption")
    return d


_CONTAINER = {"value": None}


def spec_cont(_card=None):
    return _CONTAINER["value"]


def check_shared_words(diagrams, body_text, where, lint):
    """Every name drawn on a card's diagrams must also appear in that card's text (the vocabulary rule)."""
    text = re.sub(r"<[^>]+>", " ", body_text).lower()
    for d in diagrams:
        items = d.get("nodes", []) + d.get("cols", [])
        for it in items:
            if "part" in it or not it.get("label"):
                continue
            for piece in re.split(r"\s+[·—/|]\s+|\s+and\s+|\s*\(|\)", it["label"]):
                piece = piece.strip().lower()
                if len(piece) < 4 or piece in ("nodes", "node", "program", "the", "process"):
                    continue
                if piece not in text:
                    lint.err(where, f"diagram name {piece!r} (from label {it['label']!r}) does not appear in this card's text — use the same words on the diagram and in the prose")


def diagset(diagrams):
    return f'<figure class="diagset"><script type="application/json">{json.dumps(diagrams, ensure_ascii=False)}</script></figure>'


# ---------------------------------------------------------------- lint on fragments

LINE_REF = re.compile(r"(\.(?:cc|h|hpp|py|ts|js|go|rs):\d+\b)|(\(~\d+\))|(~\d{3,}\b)")
NEGATION = re.compile(r"\b(is|are) not an? [A-Z]")
BARE_PART = re.compile(r"\bparts? [1-9]\b")
CODE_ELLIPSIS = re.compile(r"\.\.\.|…")


CROSS_PAGE = re.compile(r"\b(parts?\s+[^<]{0,40}?\bbelow|see below|next level|as above)\b", re.I)


def lint_fragment(html, where, lint):
    if where.startswith("high/") and CROSS_PAGE.search(html):
        lint.warn(where, f"cross-page pointer {CROSS_PAGE.search(html).group(0)!r} — each card stands alone; name the card instead")
    if where.startswith("high/") or where == "plain":
        for m in re.finditer(r"(?:\b(?:part|parts|to|calls|by|from|in|of)\s+)\{\{n:[a-z0-9_-]+\}\}", html):
            lint.warn(where, f"number-only chip in prose {m.group(0)!r} — use {{{{part:id}}}} so the name travels with the number")
            break
    if LINE_REF.search(html):
        lint.err(where, f"line-number anchor found: {LINE_REF.search(html).group(0)!r} — anchor with file + function + chunk name")
    if NEGATION.search(html):
        lint.warn(where, f"negation-definition: {NEGATION.search(html).group(0)!r}")
    if BARE_PART.search(html):
        lint.err(where, f"bare part number {BARE_PART.search(html).group(0)!r} — use {{{{n:id}}}} so renumbering cannot go stale")
    for m in re.finditer(r"<pre>(?:<code>)?(.*?)(?:</code>)?</pre>", html, re.S):
        code = re.sub(r'<span class="om">.*?</span>', "", m.group(1), flags=re.S)
        code = re.sub(r'<span class="c">.*?</span>', "", code, flags=re.S)
        if CODE_ELLIPSIS.search(code):
            lint.err(where, "ellipsis inside a code excerpt — cuts must be marked with <span class=\"om\">// … N lines omitted: what</span>")


# ---------------------------------------------------------------- page assembly

def article(card, level, render, num, name, lint, extra_class=""):
    where = f"{level}/{card['route']}"
    for k in ("route", "title", "hook", "body"):
        if k not in card:
            lint.err(where, f"card missing '{k}'")
    if re.fullmatch(r"(The parts|Identity|Overview|Details|The system)", card.get("title", "")):
        lint.err(where, "title is a bare label — say what the card contains")
    body = render(card["body"], where)
    lint_fragment(body, where, lint)
    diag = ""
    if card.get("diagrams"):
        resolved = [resolve_diagram(d, num, name, lint, where, spec_cont(card)) for d in card["diagrams"]]
        check_shared_words(resolved, body + " " + card.get("title", "") + " " + card.get("fn", ""), where, lint)
        diag = diagset(resolved)
        body = body.replace("{{diagrams}}", diag) if "{{diagrams}}" in body else diag + body
    fn = render(card.get("fn", ""), where)
    attrs = (f'data-route="/{level}/{card["route"]}" data-level="{level}" data-title="{esc(card["title"])}" '
             f'data-fn="{esc(re.sub("<[^>]+>", "", fn))}" data-hook="{esc(card["hook"])}" data-min="{card.get("min", 3)}"')
    return f'<article class="page{(" " + extra_class) if extra_class else ""}" {attrs}>\n{body}\n</article>\n'


def part_card(card, level, spec, render, num, name, cls, lint):
    pid = card["part"]
    cont = spec.get("container")
    is_cont = bool(cont) and pid in ("L", cont["id"])
    if not is_cont and pid not in num:
        lint.err(f"{level}/{card.get('route')}", f"unknown part '{pid}'")
        return ""
    title_prefix = cont["name"] if is_cont else f"{num[pid]} · {name[pid]}"
    card = dict(card)
    card.setdefault("route", cont["id"] if is_cont else pid)
    card["title"] = f"{title_prefix} — {card['title']}" if card.get("title") else title_prefix
    chip = "{{L}}" if is_cont else f"{{{{part:{pid}}}}}"
    other = "low" if level == "mid" else "mid"
    links = card.get("links", "")
    bar = (f'<div class="partbar">{chip}<span class="levellinks">{links}'
           f'{" · " if links else ""}<a href="#/{other}/{card["route"]}">{"Low →" if level == "mid" else "Mid ↑"}</a></span></div>\n')
    card["body"] = bar + card["body"]
    return article(card, level, render, num, name, lint)


def build(spec):
    lint = Lint()
    _CONTAINER["value"] = spec.get("container")
    render, num, name, cls = make_token_renderer(spec, lint)
    style, script = load_shell()
    cont = spec.get("container")
    title = spec["title"]

    # ---- validate part coverage
    for level in ("mid", "low"):
        have = [c["part"] for c in spec.get(level, [])]
        want = ([cont["id"]] if cont else []) + [p["id"] for p in spec["parts"]]
        for pid in want:
            if pid not in have:
                lint.err(level, f"no card for part '{pid}' — every part appears on every level")
    if len(spec["parts"]) > 8:
        lint.err("parts", "more than 8 parts — merge until each part is one job")
    if len(spec.get("map", [])) < 6:
        lint.err("map", "where-to-look needs at least 6 rows")
    if len(spec.get("principles", [])) < 4:
        lint.warn("principles", "fewer than 4 principles")

    # ---- part chips for the plain page
    chips = ''.join(f'<a class="part pL" href="#/high/parts">{esc(cont["name"])}</a>' if cont else '')
    chips += ''.join(f'<a class="part {cls[p["id"]]}" href="#/high/parts">{i + 1} · {esc(p["name"])}</a>' for i, p in enumerate(spec["parts"]))

    counts = {k: len(spec.get(k, [])) for k in ("high", "mid", "low", "traces")}
    intros = spec.get("tab_intros", {})
    home_cards = [
        ("high", "HIGH", "The world and the parts", intros.get("high", "Where it sits, what each part is responsible for, what reaches in from outside."), f'{counts["high"]} cards'),
        ("mid", "MID", "Inside each part", intros.get("mid", "Files, functions, chunk maps; how each part hands to the next."), f'{counts["mid"]} cards'),
        ("low", "LOW", "The code of each part", intros.get("low", "Verbatim excerpts beside plain English."), f'{counts["low"]} cards'),
        ("why", "PRINCIPLES", "Why it is built this way", "The choices the code rests on, each linked to the code that makes it.", "1 card"),
        ("traces", "TRACES", "Real situations", intros.get("traces", "Journeys through the parts, so the paths have a reason."), f'{counts["traces"]} cards'),
        ("map", "REFERENCE", "Where to look", "Symptom → part → function → log string.", "1 table"),
    ]
    home = f'''<section class="page" data-route="/" data-level="home">
  <h2>In plain words</h2>
  <div class="plain">{''.join(render(p, "plain") for p in spec["plain"])}</div>
  <h3>The parts — the same names on every level</h3>
  <div class="partbar">{chips}</div>
  <div class="grid">{''.join(f'<a class="card" href="#/{r}"><span class="n">{n}</span><span class="t">{t}</span><span class="h">{h}</span><span class="row"><span></span><span class="badge">{b}</span></span></a>' for r, n, t, h, b in home_cards)}</div>
  <p class="hub-intro">{render(spec.get("vocabulary", ""), "vocabulary")} Code excerpts are verbatim from this branch; cuts are marked <span class="om mono">// … omitted</span>; notes are <span class="mono" style="color:var(--note)">// ← notes</span>. Anchors are file + function + chunk name; no line numbers.</p>
</section>
'''
    hubs = ''.join(
        f'<section class="page" data-route="/{lvl}" data-level="{lvl}" data-hub="{lvl}"><h2>{h2}</h2><p class="hub-intro">{intros.get(lvl, "")}</p><div class="grid" data-cards></div></section>\n'
        for lvl, h2 in (("high", "High — where it sits and what it does"), ("mid", "Mid — inside each part"), ("low", "Low — the code of each part"), ("traces", "Traces — real situations through the parts")))

    highs = ''.join(article(c, "high", render, num, name, lint) for c in spec["high"])
    mids = ''.join(part_card(c, "mid", spec, render, num, name, cls, lint) for c in spec["mid"])
    lows = ''.join(part_card(c, "low", spec, render, num, name, cls, lint) for c in spec["low"])
    traces = ''.join(article(c, "traces", render, num, name, lint) for c in spec.get("traces", []))

    why_rows = ''.join(f'<tr><td><b>{render(p["name"], "principles")}</b></td><td>{render(p["why"], "principles")}</td><td>{render(p["where"], "principles")}</td></tr>' for p in spec.get("principles", []))
    why = f'''<section class="page" data-route="/why" data-level="why">
  <h2>Why it is built this way</h2>
  <p class="answer">Each is a choice the code rests on; each links to the Low card where it is implemented.</p>
  <div class="scroll"><table><tr><th>Principle</th><th>Why</th><th>Where it shows up</th></tr>{why_rows}</table></div>
</section>
'''
    map_rows = ''.join(f'<tr><td>{render(r["symptom"], "map")}</td><td>{render("{{L}}" if r.get("part") == "L" else "{{n:" + r["part"] + "}}", "map") if r.get("part") else ""}</td><td>{render(r["open"], "map")}</td><td>{render(r.get("grep", ""), "map")}</td></tr>' for r in spec["map"])
    mp = f'''<section class="page" data-route="/map" data-level="map">
  <h2>Where to look when something is wrong</h2>
  <p class="answer">Symptom → part → the function to open first → the string to grep.</p>
  <div class="scroll"><table><tr><th>Symptom</th><th>Part</th><th>Open</th><th>Grep</th></tr>{map_rows}</table></div>
</section>
'''
    nav = '''<nav class="levels" id="levels">
  <a href="#/" data-level="home">Plain</a>
  <a href="#/high" data-level="high">High · where it sits</a>
  <a href="#/mid" data-level="mid">Mid · inside each part</a>
  <a href="#/low" data-level="low">Low · the code</a>
  <a href="#/why" data-level="why">Why it is built this way</a>
  <a href="#/traces" data-level="traces">Traces · real situations</a>
  <a href="#/map" data-level="map">Where to look</a>
</nav>
'''
    script = script.replace("'connector-layer.done'", "document.title.replace(/\\s+/g,'-').toLowerCase() + '.done'")
    html = f'''<title>{esc(title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
{style}

<main>
<header class="top">
  <div><div class="eyebrow">Operational understanding</div><h1>{esc(title)}</h1></div>
  <div class="sha">branch {esc(spec.get("branch", ""))} · focus: {esc(spec.get("focus", ""))}</div>
</header>
{nav}
{home}
{hubs}
{highs}
{mids}
{lows}
{why}
{traces}
{mp}
<p class="tools">✓ marks live in this browser only. <button type="button" id="resetdone">Clear ✓ marks</button></p>
</main>

{script}
'''
    # ---- page-level checks
    main_js = html[html.rindex("<script>") + 8: html.rindex("</script>")]
    if re.search(r"</\s*script", main_js, re.I):
        lint.err("page", "literal </script> inside the main script block")
    # article bodies must not contain a raw <script> other than the JSON spec blocks
    for m in re.finditer(r"<script(?![^>]*application/json)", html[: html.rindex("<script>")]):
        lint.err("page", "a <script> other than the shell and JSON specs")
    return html, lint


class ScriptCheck(HTMLParser):
    """Confirm the browser sees exactly one classic script and that it holds the router."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.classic = []
        self.cur = None

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.cur = [dict(attrs), ""]

    def handle_data(self, data):
        if self.cur:
            self.cur[1] += data

    def handle_endtag(self, tag):
        if tag == "script" and self.cur:
            if not self.cur[0]:
                self.classic.append(self.cur[1])
            self.cur = None


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    html, lint = build(spec)
    p = ScriptCheck()
    p.feed(html)
    if len(p.classic) != 1 or "hashchange" not in p.classic[0]:
        lint.err("page", "the browser would not see one intact classic script block")
    out = sys.argv[2]
    open(out, "w", encoding="utf-8").write(html)
    for w in lint.warnings:
        print("WARN", w)
    for e in lint.errors:
        print("ERROR", e)
    rc = 0
    if "--no-node" in sys.argv:
        print("WARN diagram layout check skipped (--no-node)")
    elif not shutil.which("node"):
        print("WARN diagram layout check skipped: `node` is not on PATH. Install Node.js to enable it, "
              "or review the diagrams by eye before publishing.")
    else:
        rc |= subprocess.call([sys.executable, os.path.join(HERE, "diagram_check.py"), out])
    rc |= subprocess.call([sys.executable, os.path.join(HERE, "reading_time.py"), out])
    if lint.errors:
        print(f"\nBUILD FAILED: {len(lint.errors)} lint error(s). Output written to {out} for inspection only.")
        return 1
    if rc:
        print("\nBUILD FAILED: a check failed (see above).")
        return 1
    print(f"\nOK: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
