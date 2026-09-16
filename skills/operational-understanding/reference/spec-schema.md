# Spec schema — what the model writes; `scripts/build.py` writes the page

The artifact is never hand-assembled. Write `spec.json`, run
`python3 scripts/build.py spec.json out.html`, and publish `out.html` only when the build
prints `OK`. The builder assigns part numbers, chip colors, diagram labels, tab counts, card
chrome, and the shell; it refuses to emit a page that fails lint or the layout checks.

## Top level

| Key | Meaning |
|---|---|
| `title`, `favicon` | artifact name (a noun phrase) and one emoji |
| `branch`, `focus` | shown in the header: `"branch @ sha"`, `"path/to/module (Class, Class)"` |
| `container` | optional `{ "id", "name" }` — the unnumbered thing that runs the parts (a loop, a scheduler); drawn as a frame, gets the dashed chip |
| `parts` | `[{ "id", "name" }]` **in the order data meets them** — this order is the numbering everywhere |
| `plain` | list of `<p>` fragments, 4th-grade reading level, no code names |
| `vocabulary` | one line defining the everyday words used for roles |
| `tab_intros` | optional one-liners for `high`, `mid`, `low`, `traces` hubs |
| `high` | exactly two cards: *where it sits* (world arch diagram) and *the parts* (parts arch diagram + one seq per path + tables) |
| `mid`, `low` | one card **per part and per container**, keyed by `"part": "<id>"` |
| `traces` | 3–6 cards, each with one seq diagram |
| `principles` | `[{ "name", "why", "where" }]`, ≥ 4 |
| `map` | `[{ "symptom", "part", "open", "grep" }]`, ≥ 6 |

## Cards

```json
{ "route": "slug", "part": "connect",            // part only on mid/low
  "title": "dialing a main, hanging up",          // mid/low: the builder prefixes "N · Name — "
  "fn": "File.cc · FunctionA · FunctionB",        // subtitle: the function chain
  "hook": "one line for the hub card",
  "links": "in: … · out: …",                      // mid/low: shown beside the chip
  "min": 3,                                       // reading minutes; check with reading_time.py
  "body": "<html fragment>",
  "diagrams": [ …diagram specs… ] }               // optional; placed at {{diagrams}} or at the top
```

## Tokens (use these instead of typing numbers or names)

| Token | Renders |
|---|---|
| `{{part:connect}}` | numbered chip with the name: **1 Connecting & disconnecting** |
| `{{n:connect}}` | number-only chip: **1** |
| `{{L}}` | the container chip |
| `{{name:connect}}` | plain text `1 Connecting & disconnecting` |
| `{{diagrams}}` | where the card's diagram picker goes |

Writing `part 3` or `parts 2, 3` as text is a **lint error**: if the part order changes, the
tokens follow and the text would not.

## Diagram specs

Nodes and columns reference parts by id; the builder fills label and color.

```json
{ "title": "Location of the parts", "type": "arch", "rows": 4, "caption": "…",
  "cols": [{"label": "Outside"}, {"label": "FOCUS"}, {"label": "Bridge"}, {"label": "Further away"}],
  "frames": [{"label": "The loop — one pass runs 1 → 2 → 3 → 4", "col": 1, "rowFrom": 0, "rowTo": 3}],
  "nodes": [{"id": "c", "col": 0, "row": 1, "label": "Connector"},
            {"id": "p1", "col": 1, "row": 0, "part": "connect"},
            {"id": "x", "col": 3, "row": 0, "label": "RTC", "faded": true}],
  "edges": [{"from": "c", "to": "p1", "label": "knock · 5554"}] }

{ "title": "Become the driver", "type": "seq", "caption": "…",
  "cols": [{"id": "c", "label": "Connector"}, {"id": "p1", "part": "connect"}, {"id": "x", "label": "RTC", "faded": true}],
  "steps": [{"from": "c", "to": "p1", "label": "knock on 5554"}, {"from": "p1", "to": "p1", "label": "ZmqWaitForDrivebyMain"}] }
```

Rules the engine enforces (see `diagram-guide.md`): columns are locations, rows are path
order, containers are frames, edges go right/down with returns along the bottom through
gutters, one question per diagram, one picker per card.

## What the build refuses

- a part with no mid or low card; more than 8 parts
- a bare `part N` in text; an unknown part id in a token or diagram; a diagram node or column with no label
- a name drawn on a card's diagram that does not appear in that card's text (same words on the diagram, in the tables, and in the prose)
- a line-number anchor (`File.cc:123`, `(~123)`, `~1234`)
- an ellipsis inside a code excerpt outside an `<span class="om">` cut marker
- a bare-label title ("The parts", "Identity")
- a diagram whose text leaves the viewBox, whose label overflows its box, whose edge crosses a
  box, or whose edges share a vertical (from `diagram_check.py`)
- a page whose main script block would be terminated early (literal `</script>`)
- fewer than 6 map rows

Warnings (build still passes): a negation-definition ("is not a Foo"), a diagram without a
caption, fewer than 4 principles.
