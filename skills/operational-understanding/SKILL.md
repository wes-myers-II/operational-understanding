---
name: operational-understanding
description: Build an operational understanding of a subsystem, feature, or flow in any codebase and publish it as a drill-down Artifact — plain explanation, High (the world and the named parts), Mid (inside each part, file + function + chunk), Low (verbatim code beside plain English), Principles, Traces, Where to look. Use when the user wants to understand how something works well enough to explain it to anyone and navigate the code cold — "help me understand X", "walk me through X", "I need to know X before I change it", "use operational-understanding on X and the change I'm making". Asks the user pointed questions when the repo cannot answer something (unknown modules, outside systems, assumptions). Not for bug fixes, reviews, or design proposals.
---

# Operational Understanding

The reader should finish able to (1) explain exactly how the focus area works at a 4th-grade
reading level to anyone in their company, and (2) open the code and find any part of it without
help. Every artifact has the same tabs in the same order; only the contents change.

## 0. The vocabulary rule (read this first)

Before writing anything, name the **parts** of the focus area: 4–8 nouns, each with one job,
each containing named functions and owning named state. These names are used verbatim at every
level — High names them, Mid has one card per part, Low has one card per part, Traces and the
map cite steps by part. Going deeper never changes what the reader is looking at; it only adds
detail to a name they already know. If a level needs a noun the other levels don't have, the
part list is wrong; fix the list.

The number of parts is the number of jobs the code actually does, never a number chosen to fill
a level. Too many parts makes reading a chore; too few hides a job. Number the parts in the
order data meets them; a container that runs them (a loop, a scheduler) is unnumbered and is
drawn as the frame around them.

## 1. Scope and research

1. **Pin the focus.** A subsystem, a feature, or a flow. Record the branch/commit for the header.
2. **Draw the boundary.** Decide what is *inside* (this code decides it) and what is a **black
   box** (this code only sends to it, receives from it, or is gated by its state). Anything on
   the far side of a transport boundary — another process, another repo, hardware, a network peer
   — is a black box unless the user says otherwise. For a black box, record only what it accepts,
   what it returns, and what state it reports.
3. **Trace the real code.** Entry points, threads/loops, every function you will name. Delegate
   broad search to an Explore agent; read the load-bearing functions yourself.
4. **Collect anchors:** file + function for every part; the plain-English name of each chunk
   inside a large function; the log strings a reader would grep; the state each part owns.
5. **Collect the principles:** the choices the code rests on (a protocol's framing rule, a
   threading constraint, an ordering guarantee, a persistence decision). These become the
   Principles tab.
6. **Verify anything you will assert as behavior by reading the code that does it.** A claim
   from a comment or ticket is marked *verify* or removed.

### Ask when the repo cannot answer

Stop and ask the user — with `AskUserQuestion`, one to four pointed questions — whenever any of
these is true. Ask before writing, and ask again mid-write if a new gap appears. Never fill a
gap with a guess.

| Gap | Ask for |
|---|---|
| A module or dependency the focus area calls whose source is not in this repo | where it lives (another repo, a vendored lib, a service); whether to treat it as a black box; what it accepts and returns |
| An outside system that shapes behavior (a peer program, a config file written elsewhere, a deploy tool, hardware, a clock) | who owns it; what it provides; whether there is a doc or repo to read |
| An assumption you are about to encode (a default, a timeout's origin, a protocol's guarantee) that the code does not state | confirmation, or the source |
| The user has named a change ("…and the thing I want to add / remove / change") | exactly what the change is, so the *Your change* section can list what it touches |
| Two candidate part lists and the code does not settle which is right | which framing the user thinks in |

Phrase questions so the answer bridges the gap: "The focus calls `Foo::Bar` from `libfoo`,
which is not in this repo. Is that a black box for our purposes, or should I read its source —
and if so, where is it?"

## 2. Write, in the fixed tab order

Read `reference/level-rules.md` for the contents of each tab. In brief:

| Tab | Answers | Unit | Anchor |
|---|---|---|---|
| **Plain** | How would I explain this to anyone? | one short passage, 4th-grade reading level, then the part names | none |
| **High** | What world does this live in, where is the boundary, what are the parts? | processes, modules, black boxes; the parts with job / in / out / functions / state | module and component names; function names listed, not shown |
| **Mid** | Inside each part, which functions do what, in what order? | one card per part; file + function; chunk maps for large functions; hand-offs to other parts by name | `File.cc · Function · chunk name` |
| **Low** | Exactly what does this chunk's code do? | one card per part; verbatim code beside plain English | same |
| **Principles** | Why is it built this way? | the choices, each linked to the Low card that implements it | part names |
| **Traces** | What does a real situation look like through these parts? | 3–6 real journeys, steps tagged by part | part names + functions |
| **Your change** (when named) | What does my change touch? | the parts, chunks, state, and black-box contracts it affects | part names + functions |
| **Where to look** | Something is wrong — where do I start? | symptom → part → function → grep string; ≥ 6 rows | functions |

## 3. Rules that hold everywhere

- **No line numbers.** Anchor with file + function + chunk name. Chunk names are plain English
  descriptions of what a stretch of code does, with a `look for:` cue (a distinctive line).
- **Every name carries its anchor where it appears.** The reader never scrolls back.
- **Say what a thing is.** Never define by negation, and never lean on framework vocabulary
  the reader may not have: define a framework term in one clause the first time it appears.
- **Code excerpts are verbatim.** No paraphrased arguments, no `foo(...)`, no `things...`.
  Cuts are marked on their own line: `// … 6 lines omitted: what they do`. Author notes are
  `// ←` comments in a distinct color and are the only non-source text in a code block.
- **Code appears at Low**, and at Mid only when a function's shape is the explanation.
- **Diagrams come from two templates only** — the architecture grid and the sequence — built by
  the engine from declared positions. One question per diagram; one figure slot per card with a
  picker. See `reference/diagram-guide.md`.
- **Simplify at the right layer.** Mid should make a part feel as simple as it is. Black boxes
  stay black; the reader is told what crosses the boundary, never what happens inside.

## 4. Build and publish

**Never hand-assemble the HTML.** Write the content spec; the builder writes the page.

1. Load the `artifact-design` skill (mandatory before writing any artifact).
2. Write `spec.json` per `reference/spec-schema.md`: title, branch, focus, the container and
   the parts (in path order — this order is the numbering everywhere), the plain passage, two
   High cards, one Mid and one Low card per part, traces, principles, map. Text uses tokens
   (`{{part:id}}`, `{{n:id}}`, `{{L}}`) instead of typed numbers or names; diagrams are `arch` /
   `seq` specs whose nodes reference parts by id. Card bodies are HTML fragments; code excerpts
   verbatim with `<span class="om">// … N lines omitted: what</span>` cut markers.
3. Run `python3 scripts/build.py spec.json out.html`. It assembles the page from
   `templates/drilldown.html` (shell, router, diagram engine, lightbox), assigns every part
   number, chip, and diagram label from the parts list, then lints (bare part numbers,
   line-number anchors, ellipses in code, bare-label titles, missing part cards, unknown ids,
   `</script>` inside the script block) and runs `diagram_check.py` (text in bounds, labels in
   boxes, no edge through a box, no coincident verticals; needs node) and `reading_time.py`
   (every card ≤ 5 min). It prints `OK` or refuses. Fix the spec, never the output.
4. Publish `out.html` with the Artifact tool. Title = the subsystem's name. Favicon on first
   publish. On revision, edit the spec, rebuild, redeploy the same file path.

## 5. Quality gate

- [ ] The part list is the same on High, Mid, Low, Traces, and the map.
- [ ] The Plain passage can be read aloud to someone outside engineering.
- [ ] Every black box is named as one, with what crosses its boundary.
- [ ] Every gap was asked about, not guessed; answers are reflected in the text.
- [ ] Every function named exists on the stated branch; every excerpt is verbatim.
- [ ] No line numbers; no negation-definitions; no undefined framework terms.
- [ ] Principles each link to a Low card; each Low card links up to its Mid card.
- [ ] Where-to-look has ≥ 6 rows with grep strings.
