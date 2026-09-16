# Level rules

The artifact has fixed tabs in a fixed order. A small set of named **parts** is decided once
and used verbatim on every tab (see SKILL.md §0). This file says what goes on each tab.

## Plain

One passage, 4th-grade reading level, no code names: who the actors are, what the system does
for them, the two or three rules that make it behave the way it does. Everyday words for the
roles ("driver", "helper", "checkpoint", "door") are encouraged here and may be reused in prose
elsewhere alongside the code names. End with the part names as chips, so the reader sees the
vocabulary before the first level.

## High — the world and the parts

Two cards:

**The world, and where the boundary is.** Name the processes, modules, and outside programs
that exist, using the codebase's own terms and defining each framework term in one clause
(e.g. what a "Node" or an "Application" is in this framework). One diagram: boxes are
processes/modules, edges are the transport between them (protocol, topic, file). State
explicitly what this subsystem is responsible for and how far each other thing is from it; for each far thing,
what it accepts, returns, and reports. A table: component → kind → responsible for.

**The parts.** One figure slot with a picker: first the **architecture grid** of the parts
(columns = locations, rows = path order, the container drawn as a frame), then **one sequence
diagram per thing an outside actor can do** (become the driver, send a command, get the
answer, …). See `diagram-guide.md`. Under it, a table: what happens → path through the parts
(chips) → functions in order; then the parts table: part → job → in → out → functions it
contains → state it owns. Function and member names appear here so Mid attaches to them; nothing about
how they work. Close with "what reaches in from outside, by part".

Detail level — **fade by relevance**: the further a thing is from the focus, the more opaquely it is described — and the reader is never told this; no "faded", "black box", or "further away" on the page. Far things get one line ("RTC acts on request topics and publishes replies");
near things get their names. The reader should not need to know how a far component works to
understand this subsystem.

## Mid — inside each part

One card per part, same name, same order, with the part chip and a one-line restatement of
in/out at the top. Then:

1. **Where block**: file · function signature · who calls it / what starts it.
2. **Steps or a chunk map.** For a chain of small functions: numbered steps, each
   `File.cc · Function` → one plain sentence → state touched. For a large function: a **chunk
   map** — 3–7 named chunks in reading order, each with a `look for:` cue (a distinctive line
   the reader can search for). Chunk names are plain English ("make sure we have a main").
3. **Hand-offs** to other parts, by part name and number ("→ part 5").
4. **Branches** shown in the same list, marked as such.
5. A small table when the part has parallel outcomes (which branch → which state → which log).
6. Link to the part's Low card.

Code appears here only when a function's shape *is* the explanation (a dispatch switch).

## Low — the code of each part

One card per part, same name. For the chunk in that part that is hardest to read cold: the
verbatim code on the left, plain English on the right, one paragraph per statement group.
Cuts marked `// … N lines omitted: what`. Link up to the Mid card and across to the Principles
that the code implements. Cross-branch notes when the code differs between branches.

## Principles — why it is built this way

One table: principle → why (two or three sentences, more generic than Low, including the
cost of the choice) → where it shows up (part chip + link to the Low card). Typical entries:
a protocol's framing rule, a threading constraint, an ordering guarantee, a persistence
decision, a security stance and its limit. Six to ten rows.

## Traces — real situations

Three to six real journeys through the parts. Each: the actor and what crossed the wire; the
steps, each tagged with the part chip and the function; a state table (field → value → so).
One sequence diagram at most, only where the ordering is the point. Traces make the branches
in Mid feel necessary rather than arbitrary.

## Your change (only when the user has named one)

Which parts, chunks, state fields, and boundary contracts the change touches; which Traces
exercise them; which tests cover them. Written in the same part vocabulary.

## Where to look

Symptom → part chip → first function to open → string to grep. At least six rows. This is the
table the reader returns to.

## Numbering the parts

Parts are numbered in the order data meets them along the main path (row order on the
architecture grid), so "1 → 2 → 3" reads as the flow. A container that runs the parts (a loop,
a scheduler) is **unnumbered** and drawn as the frame around them; it gets the dashed
container chip (`part pL`).

## Titles

A card title says what the card contains, so the hub can be scanned without opening anything:
"3 · Identity — which connection is main, which is aux", "Where the connector layer sits in the
system", "Where to look when something is wrong". Never a label alone ("The parts", "Identity").
Tab labels carry the same information in three or four words ("Mid · inside each part").

## Anchoring, language, code — the rules that hold everywhere

- No line numbers. File + function + chunk name.
- Every proper noun carries its anchor where it appears.
- **Each card stands alone.** Never point at another card with "below", "above", or "next"
  as if it were on the same page; name the card ("the parts card lays them out", "the Mid
  cards show how"). Restating the web of connections at a high level on more than one card is
  welcome — that repetition is how the reader ties the pages together.
- **In prose, parts go by name** (`{{part:id}}` — the numbered chip with the name). Number-only
  chips (`{{n:id}}`) belong in path strips, tables of steps, and the map, where the sequence is
  the point; a number alone in a sentence sends the reader hunting.
- Say what a thing is; define framework terms on first use; no negation-definitions.
- Verbatim code only; explicit cuts; `// ←` author notes in a distinct color.
- Diagrams only where a table cannot do the job.
- Every card under 5 minutes by `scripts/reading_time.py`.
