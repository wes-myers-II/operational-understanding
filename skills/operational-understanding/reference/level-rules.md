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

Include:
- **The pieces** table: components / processes / threads / boundaries (sockets, endpoints,
  queues, topics) / external actors, one line each with its purpose and direction (who calls
  whom, who initiates).
- **The state model**: every piece of persistent state that defines "what the system thinks is
  true," grouped by category, one line each. If two fields look alike, say how they differ.
- **The spine**: the one loop / lifecycle / pipeline that everything else hangs off, as a
  numbered list in execution order.
- **Key insights** as callout boxes: the 2–4 facts that make the mid level make sense.
- **One diagram**: architecture (boxes/wires) or the spine as a flow.
- Closing line: "What I simplified here: …"

Exclude: function-by-function narration, code excerpts, field-by-field tables.

## Mid level — "functions and module flow"

Answer: which functions run, in what order, reading/writing which state, for each scenario a
reader will actually encounter. A reader who stops here can open the code and navigate.

Structure as **scenarios**, each told as actor action → boundary → system state:
1. **Trigger**: what the human/client/upstream system did, and what literally crossed the
   boundary (protocol, port, endpoint, message or event type, payload if it matters).
2. **Path**: the functions in call order. For each: one clause on what it does, the condition
   that selects it, and the state it touches. Parameters that come from somewhere non-obvious
   get a "from:" note.
3. **State table**: field → before → after → what that value now causes.
4. **Branches**: where the path forks (success/failure, race), show both.
5. **Link down**: any step compressed here links to its Low section.

Diagram per scenario: `sequenceDiagram` for multi-party time flow, `stateDiagram-v2` for
lifecycle, `flowchart` for decision-heavy logic. Messages/edges use real function names and
real condition text.

Closing line per scenario or per level: "What I simplified here: …"

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
