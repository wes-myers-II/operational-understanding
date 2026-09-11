# Level rules

Three levels, each self-sufficient for a different reader mode. The same topic appears at all
three; what changes is the unit of explanation and how much is deferred to the level below.

## Reading-time budget

Estimate at 220 words/minute for prose, 90 words/minute for code excerpts, +30 s per diagram,
+20 s per table. `scripts/reading_time.py` computes this from the HTML.

| Unit | Limit |
|---|---|
| one section (an `<h2>`/`<h3>` block with a badge) | ≤ 5 min; target 2–4 |
| High level total | ≤ 10 min |
| Mid level total | ≤ 20 min |
| Low level total | uncapped, but every section ≤ 5 min and reachable from a mid-level link |
| whole artifact (stated at the top) | give a number; also state "High only: N min" |

If a section is over, split by scenario or by mechanism — never by cutting the state table or
the key insight.

## High level — "the whole thing in one flow"

Answer: what is this, what are its moving parts, how does one complete interaction pass
through it, and what state does it keep. A reader who stops here should be able to have a
design conversation about it.

Four cards, in this order:
- **The pieces**: architecture diagram (who talks to whom, who initiates) + a table of
  component / owner / does.
- **The lifecycle**: the states the code actually names, as a flow strip and a
  `stateDiagram-v2`; one callout on the transition that people get wrong.
- **The state, grouped**: every field that defines "what the system thinks is true," as 3–5
  boxes, each box one question ("who is connected right now", "where to dial next"). If two
  fields look alike, say how they differ, inside the box.
- **The facts to carry**: the 2–4 insights as boxes with bullets and a link into Mid.
- Closing line: "What I simplified here: …"

Exclude: function-by-function narration, code excerpts, field-by-field tables.

## Every page, at every level — scannable before it is readable

A reader who does not read a single paragraph must still see the flow. Every card opens in
this order, no exceptions:

1. **Answer line** — one bold sentence: what this page tells you.
2. **Flow strip or diagram** — the mechanism as ordered tiles (`number · FunctionName · one
   clause`) or a Mermaid flowchart whose nodes are function names. Branch tiles marked `alt`;
   terminal/failure tiles marked `stop`.
3. **Table** — function → does → reads → writes (or field → before → after → so).
4. **Prose** — folded inside `<details><summary>Narrative</summary>`. Optional.

Prose outside the fold is limited to the answer line, captions, and callouts. If a page needs
a paragraph to be understood, the strip is wrong; fix the strip.

## Mid level — "mechanisms"

Answer: which functions run, in what order, reading/writing which state. The unit is the
**mechanism** — one function chain that does one job (the main loop, getting connected,
identifying a sender, dispatching, replying, streaming, handoff, teardown). One card per
mechanism; the card's subtitle is the chain itself (`A → B → C`).

Scenarios are **not** the load-bearing structure. They live in a separate **Traces** tab: a
real situation run through the mechanisms — actor, wire, sequence diagram, state table — each
linking back to the mechanism cards it exercises. Six or fewer.

Diagram choice: `flowchart` with real condition text for decision chains, `sequenceDiagram`
for traces and handoffs, `stateDiagram-v2` only when the states are named in code.

Closing line per level: "What I simplified here: …"

## Low level — "the place to go when a mid step didn't land"

Answer: show me exactly. Each Low section serves one mid-level step or one mechanism.

Include:
- Annotated code excerpt (real, from the stated branch, trimmed to the relevant lines).
  Annotate *why*, not *what*: the invariant, the ordering constraint, the failure it prevents.
- Field-by-field table when a function sets/clears several members.
- The exact conditions (quote them) for any branch the mid level summarized.
- Threading/ordering notes when two contexts touch the same state.
- Cross-branch notes if the topic exists in more than one branch ("on main X; on branch Y").

Mandatory final section — **Navigation map**:

| Symptom / question | First function to open | Log string to grep |
|---|---|---|

At least six rows. This is the table the reader will actually return to.

## Callout kinds (use the template's classes)

- `insight` — a fact that reorganizes the mental model.
- `gotcha` — a behavior that bites in the field.
- `simplified` — "I compressed this; the full version is at <link>."
- `verify` — a claim sourced from a comment/ticket, not from reading the executing code.

## Voice

Direct, declarative, present tense. Say what the system does, not what you did. No hedge-by-
negation ("this is not X"); state what it is. One idea per paragraph. Tables over prose when
there are more than three parallel facts.
