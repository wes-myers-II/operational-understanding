---
name: operational-understanding
description: Build a three-level (high / mid / low) operational walkthrough of a subsystem, flow, or module and publish it as a blog-style Artifact with diagrams, reading-time badges, and a "where to look" navigation map. Use when the user wants to *understand how something works end to end* well enough to navigate it with ease — "walk me through X", "how does X actually work", "give me operational understanding of X", "I need to know this system before I change it", or when starting design work on a subsystem they don't yet own. Not for bug fixes, code review, or design proposals; it produces understanding, not changes.
---

# Operational Understanding

Produce the document a senior engineer wants before touching a subsystem: enough context to
navigate it cold, know which ten functions matter, and find any detail trivially when needed —
without getting lost in the weeds. Output is a blog-style Artifact with three nested levels,
diagrams at each, and every claim verified against the code.

## The reader's ethos (this is the definition of done)

- Whole-system context first; details on demand. Reading it should make the code *navigable*,
  not memorized.
- Explicit where a wrong mental model would cause a wrong change. Simplified only at the layer
  below what the reader needs to act on — and say so when you simplify.
- Never lost in the weeds: every section readable in one sitting without fatigue.
- When the reader doesn't know a detail after reading, finding it must be trivial: function
  names, file names, log strings to grep.

## Method

### 1. Scope and research (do not write yet)

1. Pin the target: a flow ("session handoff between two clients"), a module ("the gateway
   service"), or a mechanism ("the background ingest thread"). Confirm the branch/commit — state
   it in the artifact header. Mixing branches silently is the most common way these documents go
   wrong.
2. Trace the real code. Read the entry point, follow calls, read every function you will name.
   Delegate broad tracing to a fork/Explore agent; read the load-bearing functions yourself.
3. Collect **anchors**: `File::Function` for every mechanism, the exact log strings a reader
   would grep for, the state (members/flags/maps) that the mechanism reads or writes.
4. Hunt for the **key insights** — facts that reorganize the reader's mental model (e.g.
   "'connected' happens in two stages, transport then registration", "identity is derived from the
   connection, never from the payload", "this reply is asynchronous and arrives on a different
   thread"). Usually 2–4 per topic. These become callout boxes.
5. Verify anything you are about to assert as behavior by reading the code that does it. If a
   claim came from a comment, a ticket, or memory, mark it as such or verify it.

### 2. Write the three levels

Read `reference/level-rules.md` for what belongs at each level and the chunking rules. Summary:

| Level | Question it answers | Unit of explanation | Diagram |
|---|---|---|---|
| **High** | What is this and how does it flow end to end? | subsystems, processes/threads, boundaries (sockets, APIs, queues), state categories | one architecture/flow diagram |
| **Mid** | Which functions do what, in what order, touching which state? | functions, modules, state tables | sequence / state / flowchart per scenario |
| **Low** | I didn't follow a mid-level step — show me. | code excerpts, field-by-field tables, exact conditions | annotated excerpt, small focused diagram |

Rules that hold at every level:
- Each section carries a reading-time badge and stays under ~5 minutes (see level-rules for the
  formula). Split rather than compress.
- Function names are the primary anchor. Line numbers are allowed as `(~NNN)` and labeled as
  volatile; never make a claim depend on one.
- Scenarios are told as **actor action → boundary (wire / API call / event) → system state**,
  with a state table after any multi-step transition.
- The Low level ends with a **navigation map**: symptom → first function to open → log string.
- Mid → Low cross-links: every mid step that compresses something links to the low section that
  expands it.
- Name what you deliberately simplified, in one sentence, at the end of each level.

### 3. Diagrams

Read `reference/diagram-guide.md`. Choose the diagram by what the reader must *see*:

- **Flow through time between parties** → Mermaid `sequenceDiagram` (handoffs, handshakes, request/reply).
- **State that changes** → Mermaid `stateDiagram-v2` (connection lifecycle, flags).
- **Boxes and wires / who talks to whom** → inline SVG via the `artifact-diagramming` skill
  (architecture, processes, threads, queues, sockets). Mermaid `flowchart` is acceptable for a
  first draft.
- **Decision logic** → Mermaid `flowchart` with the real condition text on the edges.

Mermaid renders natively in Artifacts (`<pre class="mermaid">`), no library. Excalidraw is
**not installed** on this machine; if the user wants to experiment with it, see the guide's
"experimental backends" section before promising anything. Every diagram gets a one-line caption
stating what to notice.

### 4. Build and publish the artifact

1. Load the `artifact-design` skill (mandatory before writing any artifact).
2. Start from `templates/blog.html`. Fill: title, one-sentence purpose, branch/worktree, total
   reading time, TOC, the three levels, navigation map, "what changed / what this replaces" if
   the topic is being redesigned.
3. Run `scripts/reading_time.py <file.html>` and paste the numbers into the badges. Re-split any
   section over the limit.
4. Publish with the Artifact tool. Title = the subsystem name (e.g. "Session Layer",
   "Ingest Pipeline"), not a summary. Favicon once on first publish.
5. On revisions, redeploy the same file path.

### 5. Quality gate (check before publishing)

- [ ] Every function named exists on the stated branch (grep it).
- [ ] Every scenario ends in a state table or an explicit "state unchanged".
- [ ] Key insights are called out, not buried in prose.
- [ ] Navigation map present, at least 6 rows.
- [ ] No section badge over the limit; total time stated at the top.
- [ ] Each level ends with its "what I simplified" line.
- [ ] Diagrams have captions; sequence diagrams show the *real* function names as messages.
- [ ] No hand-wave verbs ("commits", "handles", "checks") without saying what is done.

## Anti-patterns (each of these has made a reader stop trusting the document)

- Listing function names as if naming them explained them.
- Line numbers without a filename.
- A "call sequence" with no explanation of callers, parameters, or where values come from.
- Prose that narrates the author's process ("I traced…") instead of the system.
- Claiming a fix, a bug, or a behavior from a comment without reading the code that does it.
- Mixing two branches' code without saying so.
