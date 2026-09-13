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
  dashed lane. Two edges may never cross; if a picture needs a crossing, it is two diagrams.
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

## Verify before publishing

Extract `renderArch`/`renderSeq` from the page and run them over every spec in node: assert no
`<text>` lands outside the viewBox and no node line exceeds the node width. Also assert the
page's main `<script>` block contains no literal `</script>` — a JS comment mentioning one will
terminate the block and print the rest of the script as page text.
