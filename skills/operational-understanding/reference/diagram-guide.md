# Diagram guide

Diagrams are built by the template's engine from JSON specs. **No auto-layout, ever**: every
box has a declared column and row. Two diagram templates cover everything; each answers one
question; a card holds one figure slot with a picker (buttons + prev/next + full screen) so a
page never shows more than one diagram at a time.

## Template 1 — architecture grid (`"type": "arch"`)

Answers: *where does each thing live, and what moves between them?*

- **Columns are locations**, declared left → right by distance from the actor: outside the
  system · the process holding the focus · the bridge · the black boxes. The same columns on
  every arch diagram in the artifact.
- **Rows are path order**: row 0 is where data enters; each part sits in the row it is first
  reached. Parts are **numbered in this order**, so the numbers read top to bottom.
- **A container is a frame, never a box.** A loop or scheduler that runs the parts is drawn as
  a dashed frame around them with its label ("The loop — one pass runs 1 → 2 → 3").
- **Edges go right or down.** A return (to an earlier column) is routed along the bottom as a
  dashed lane. Solid edges never cross each other; a dashed return may cross a solid edge only
  at a right angle; no two edges run coincident; no edge passes through a box. If two solid
  edges would cross, it is two diagrams.
- **Edge labels say what moves and over what** ("command · 5555", "reply · kRequestReplyTopic").
- Black boxes get `"black": true` (dashed border). Parts get `"part": N` for their color;
  the container gets `"part": "L"`.

```json
{"title":"Location of the parts","type":"arch","rows":3,"caption":"…",
 "cols":[{"label":"Outside"},{"label":"FOCUS"},{"label":"Bridge"},{"label":"Black box"}],
 "frames":[{"label":"CONTAINER — one pass runs 1 → 2 → 3","col":1,"rowFrom":0,"rowTo":2}],
 "nodes":[{"id":"a","col":0,"row":1,"label":"actor"},{"id":"p1","col":1,"row":0,"label":"1 PART","part":1}],
 "edges":[{"from":"a","to":"p1","label":"input · transport"}]}
```

## Template 2 — sequence (`"type": "seq"`)

Answers: *for one thing an actor can do, what happens in what order?*

- **Columns are the actors and parts**, in the same order and colors as the arch grid.
- **Rows are steps in time**, numbered. An arrow is a hand-off; a box on a column is work
  inside that part, labeled with the function and what it decides.
- **A loop back is visible**: a later row whose arrow points to an earlier column.
- One sequence per path (become the driver, send a command, get the answer, …). Never merge
  paths into one sequence.

```json
{"title":"Do X","type":"seq","caption":"…",
 "cols":[{"id":"a","label":"actor"},{"id":"p1","label":"1 PART","part":1},{"id":"x","label":"black box","black":true}],
 "steps":[{"from":"a","to":"p1","label":"input · transport"},{"from":"p1","to":"p1","label":"Function: decision"},{"from":"p1","to":"x","label":"output"}]}
```

## Where they go

| Card | Figure slot holds |
|---|---|
| High · where it sits | one arch: the world (processes, bridge, black boxes, transports) |
| High · the parts | one arch (location of the parts) + one seq per path, in the same picker |
| Traces | one seq per trace |
| Mid / Low | none by default; a chunk map or table does the job |

## Text fits, always

The engine wraps labels to the box and sizes rows, columns and steps from the wrapped text.
Keep labels short anyway; put explanation in the caption. A single word longer than ~26
characters will not fit a node — shorten it or split it.

## How the engine routes edges (so specs stay readable)

- Forward edges (to a column further right) leave the source's right side and enter the
  target's left side. Several departures from one box fan out vertically; several arrivals into
  one box fan in. An elbow edge's label sits on the segment that belongs only to that edge.
- Same-column edges run straight down the column center with the label to the right.
- Return edges (to a column further left) leave the source's right side into a gutter beside
  the column, run along a dashed lane below the grid, climb the gutter left of the target's
  column, and enter the target's left side — never through another box.
- The gap between two columns is split into three bands so edge kinds never share an x:
  forward elbows (30–55 % of the gap), return arrivals (62–78 %), return departures (84–96 %).
  Elbow labels end just before the target box rather than centering on a short segment.

## Verify before publishing

Run `scripts/diagram_check.py <file.html>` (node required). It fails on text outside the
viewBox, a node line wider than its box, an edge segment passing through a box, or a literal
`</script>` inside the page's main script block (a JS comment mentioning one terminates the
block and the rest of the script prints as page text).
