# operational-understanding

A Claude Code skill for understanding a subsystem, feature, or flow in any codebase well enough
to explain it to anyone and navigate the code cold. It publishes a drill-down Artifact with a
fixed set of tabs and a fixed vocabulary of **named parts** that is carried through every level,
so going deeper never changes what you are looking at:

| Tab | What it holds |
|---|---|
| **Plain** | the whole thing in everyday words, then the part names |
| **High** | the world by name — processes, modules, framework terms defined once, black boxes drawn explicitly — then each part's job, inputs, outputs, functions, state |
| **Mid** | one card per part: file + function, large functions broken into plain-English chunks with a `look for:` cue (no line numbers) |
| **Low** | one card per part: verbatim code beside plain English |
| **Principles** | the choices the code rests on, each linked to the code that implements it |
| **Traces** | real situations followed through the parts |
| **Where to look** | symptom → part → function → log string |

When the repository cannot answer something — a module whose source lives elsewhere, an outside
system that shapes behavior, an assumption the code does not state — the skill stops and asks you
pointed questions instead of guessing.

It produces understanding, not changes. Use it before you redesign something you don't yet own.

## Install

As a plugin (recommended — gets updates):

    /plugin marketplace add wes-myers-II/operational-understanding
    /plugin install operational-understanding@operational-understanding

Or copy the skill directly:

    git clone https://github.com/wes-myers-II/operational-understanding.git
    cp -R operational-understanding/skills/operational-understanding ~/.claude/skills/

Or vendor it into one project so teammates get it with the checkout:

    cp -R operational-understanding/skills/operational-understanding <repo>/.claude/skills/

## Use

    /operational-understanding <subsystem, feature, or flow>
    /operational-understanding <subsystem> and the change I'm making: <what>

## Requirements

| Needed for | Requirement | If missing |
|---|---|---|
| building the page | Python 3.9+, standard library only | — |
| the diagram layout check | `node` on PATH | build still runs; it warns that the check was skipped |
| publishing as a claude.ai artifact | the Claude Code Artifact tool | the output is one self-contained HTML file; open it in a browser or host it anywhere |
| design calibration | the built-in `artifact-design` skill | skipped if not present; the template carries the design |

No external services and no CDN-loaded libraries except Google Fonts (with system fallbacks):
diagrams are drawn by a small deterministic engine inside the page from declared positions —
no auto-layout, no Mermaid.

Verify a checkout works before relying on it:

    python3 skills/operational-understanding/scripts/build.py \
        skills/operational-understanding/templates/example.spec.json /tmp/example.html
    # expect: OK: /tmp/example.html

## How a page is made

The model never hand-assembles HTML. It writes a content spec (parts in path order, cards,
diagram specs, text with `{{part:id}}` tokens) and runs

    python3 skills/operational-understanding/scripts/build.py spec.json out.html

The builder assembles the page from the template shell, assigns every part number, chip,
and diagram label from the one parts list, lints the content (bare part numbers, line-number
anchors, ellipses in code, bare-label titles, missing part cards, unknown ids), runs the
diagram layout check and the reading-time budget, and refuses to emit a page that fails.

## Layout

    skills/operational-understanding/
      SKILL.md                     method: vocabulary rule, boundary, ask-at-gaps, tab order, build, quality gate
      reference/level-rules.md     what belongs on each tab
      reference/diagram-guide.md   the two diagram templates (architecture grid, sequence) and routing rules
      reference/spec-schema.md     the content spec the model writes
      templates/drilldown.html     the page shell: CSS, router, diagram engine, lightbox
      templates/example.spec.json  a minimal neutral spec that builds
      scripts/build.py             spec → page, with lint and checks
      scripts/diagram_check.py     layout check for the diagrams (needs node)
      scripts/reading_time.py      per-card minutes; fails if a card is over 5 minutes

## License

MIT — see `LICENSE`.
