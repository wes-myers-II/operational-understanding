# operational-understanding

A Claude Code skill that builds a three-level operational walkthrough of a subsystem —
**high** (the whole flow, end to end), **mid** (functions and module flow per scenario),
**low** (exact mechanisms, for when a mid-level step didn't land) — and publishes it as a
blog-style Artifact with diagrams, per-section reading-time budgets, and a
symptom → first-function-to-open → log-string navigation map.

It produces understanding, not changes: use it before you redesign something you don't yet own.

## Install

As a plugin (recommended — gets updates):

    /plugin marketplace add <your-github-or-bitbucket>/operational-understanding-plugin
    /plugin install operational-understanding@operational-understanding

Or copy the skill directly:

    git clone <repo-url>
    cp -R operational-understanding-plugin/skills/operational-understanding ~/.claude/skills/

Or vendor it into one project so teammates get it with the checkout:

    cp -R operational-understanding-plugin/skills/operational-understanding <repo>/.claude/skills/

## Use

    /operational-understanding <subsystem, flow, or module>

Requires the Claude Code Artifact tool (for publishing) and the built-in `artifact-design` /
`artifact-diagramming` skills (loaded automatically by the skill). Diagrams render with Mermaid,
which Artifacts support natively; no external services.

## Layout

    skills/operational-understanding/
      SKILL.md                    method, quality gate, anti-patterns
      reference/level-rules.md    what belongs at each level; reading-time budget
      reference/diagram-guide.md  which diagram for which content; backends
      templates/blog.html         themed skeleton
      scripts/reading_time.py     per-section minutes; exits 1 if a section is over budget
