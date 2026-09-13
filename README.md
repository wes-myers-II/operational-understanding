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

Requires the Claude Code Artifact tool (for publishing) and the built-in `artifact-design`
skill, which the skill loads itself. Diagrams render with Mermaid, which Artifacts support
natively; no external services.

## Layout

    skills/operational-understanding/
      SKILL.md                    method: vocabulary rule, boundary, ask-at-gaps, tab order, quality gate
      reference/level-rules.md    what belongs on each tab
      reference/diagram-guide.md  which diagram for which content
      templates/drilldown.html    the one-screen-at-a-time app shell (default)
      templates/blog.html         single-page fallback
      scripts/reading_time.py     per-card minutes; exits 1 if a card is over 5 minutes

## License

MIT — see `LICENSE`.
