# Level rules

The goal of an operational-understanding artifact: the reader understands the focus area so
well they can explain exactly how it works at a 4th-grade reading level to anyone in the
company, and can open the code and find any part of it without help.

The structure is fixed. Every artifact has the same sections in the same order. Only the
contents vary. This is what makes the output deterministic and lets the reader ask for it
casually ("use this skill to help me understand X and the change I'm making to it").

## Fixed structure

| Section | Question it answers | Unit of explanation | Anchor style |
|---|---|---|---|
| **Plain explanation** | How would I explain this to anyone? | one paragraph, 4th-grade reading level | none — no code names |
| **High** | Where does this sit in the whole system, and what does data flow through to reach it? | modules, processes, subsystems, external systems | module / process / directory names |
| **Mid** | How does data move from outside the system into the focus area, and what happens to it there? | functions, broken into named logical chunks | `File.cc` + `Function` + chunk name |
| **Low** | This mid chunk is confusing — what exactly does the code do? | verbatim code next to plain English | `File.cc` + `Function` + chunk name |
| **Your change** (when the user names one) | What does my add/remove/change touch? | the mid chunks, state, and external contracts it affects | as above |
| **Where to look** | Something is wrong — where do I start? | symptom → function → grep string | `File.cc` + `Function` |

Optional appendix: **Traces** — a real situation followed through the mid chunks, when a
branch cannot be understood from a single reading. Never a level; never the organizing unit.

## Anchoring

- **No line numbers.** They go stale. Anchor with file and function; inside a large function,
  anchor with the chunk name, which is a plain-English description of what that stretch of
  code does ("the chunk that tries known addresses before listening").
- Every proper noun carries its anchor **where it appears**, every time — function
  (`RequestClerk.cc · ReceiveRouterMessage`), member (`RequestClerk.h · identity_to_role_`),
  external thing (`ROS2 topic kRequestReplyTopic, published by RTC`). The reader must never
  scroll back to find what something is.
- Assume the reader is a competent engineer. Do not assume they know this codebase's
  framework vocabulary: define a framework term in one clause the first time it appears, and
  say what a thing **is**, never what it is not.

## Code excerpts

- Verbatim lines only, copied from the stated branch. No paraphrased arguments, no `foo(...)`,
  no `caches...`. If a stretch is cut, mark it on its own line:
  `// … 6 lines omitted: assigns the cache pointers passed in`.
- Author notes are comments in a distinct color, prefixed `// ←`, and are the only non-source
  text inside a code block.
- A code block appears at the Low level, and at the Mid level only for a function whose shape
  *is* the explanation (a dispatch loop, a switch). Everywhere else, name the function and
  describe the chunk.

## High level — "the system as a whole"

Two or three cards:
- **The system**: the processes/modules that exist, and where the focus area sits. One
  diagram of boxes = modules/processes, edges = the transport between them (protocol, topic,
  file). Table: module → directory → what it owns.
- **The path**: the subsystems data passes through from the outside world to the focus area
  and back, in order, one line each. This is the spine the mid level expands.
- **External systems**: anything outside this code that affects how it runs (other programs,
  network peers, files on disk, hardware, timers) — what it provides, and which module in the
  path consumes it.

No functions at this level except the entry point.

## Mid level — "how data moves into the focus area"

One card per **flow** — one path data takes from outside to inside (a connection being made,
a request being handled, a reply going back, a control handoff). Each card:
1. Answer line: what moves, from where, to where.
2. The flow as ordered steps. Each step = `File.cc · Function` (+ chunk name for big
   functions) → one plain sentence of what that chunk does → what it reads/writes.
3. For big functions: a **chunk map** — the function's body split into 3–7 named chunks, in
   order, so the reader can open the function and locate each by reading.
4. Branches: where the flow forks, both outcomes, in the same step list.
5. Link down: any chunk that needs the exact code links to its Low card.

Simplify here. The mid level should make the flow feel as simple as it actually is. If a
flow needs more than ~8 steps, it is two flows.

## Low level — "exactly what the code does"

One card per confusing chunk. Two columns or two stacked blocks: the verbatim code, and a
plain-English walk of it, sentence per statement group. Say which mid step it serves.
Cross-branch notes when the code differs between branches.

## Reading-time budget

`scripts/reading_time.py` reports per-card minutes: 220 wpm prose, 90 wpm code, +30 s per
diagram, +20 s per table. Keep every card under 5 minutes; split by flow or chunk, never by
cutting an anchor.

## Voice

Direct, declarative, present tense. Plain words. One idea per sentence. Tables over prose for
parallel facts. The plain explanation at the top is the test of the whole document: if it
cannot be written simply, the understanding is incomplete.
