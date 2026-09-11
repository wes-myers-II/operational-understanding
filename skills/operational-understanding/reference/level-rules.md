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

## Mid level — "mechanisms, grounded in the code"

Answer: which functions run, in what order, reading/writing which state — shown with the
**real code**, so the reader can open the file and recognize it. The unit is the
**mechanism** — one function chain that does one job (the main loop, getting connected,
identifying a sender, dispatching, replying, streaming, handoff, teardown). One card per
mechanism; the card's subtitle is the chain itself (`A → B → C`).

Every mid card, in order:
1. Answer line.
2. **Where block**: file · function signature · line · called from · calls. This is the
   reader's map into the source; it is the most important element on the card.
3. **The real function body, trimmed** to its decisions, with the author's notes as
   `// ←` comments in a distinct color. Paraphrased pseudo-flow is not a substitute:
   readers who know the code recognize real code and distrust paraphrase.
4. Table: callee → line → reads → writes, or field → before → after.
5. Prose only in callouts or folded.

Mid level total may exceed the 20-minute budget when the excess is code; keep each card
under 5 minutes.

## Language rules (from reader feedback)

- Say what a thing **is**. Do not define by negation ("this is not an X") — especially when
  the reader may not know X. If a framework term is needed, define it in one clause the first
  time it appears ("an ATK Node — the framework's unit that owns ROS2 publishers").
- Say obvious things plainly. Subtlety that the reader must infer is a defect.
- A diagram earns its place only when a table cannot show the same thing. Prefer the code
  excerpt, then the table, then the diagram. Three or four diagrams in a whole artifact is
  typical.

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
