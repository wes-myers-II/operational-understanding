# Diagram guide

A diagram earns its place only when a table cannot show the same thing. Two or three per
artifact is typical. Every diagram gets a one-line caption saying what to notice.

## Where diagrams belong

| Tab | Diagram | What it shows |
|---|---|---|
| High · the world | one `flowchart` | processes / modules / outside programs as boxes; the transport between them (protocol, topic, file) on the edges; black boxes labeled as such |
| High · the parts | one `flowchart` | the named parts as boxes; dotted edges for "called every cycle", solid edges for data moving; where outside data enters |
| Traces | at most one `sequenceDiagram`, only where ordering across two passes or two parties is the point | the actors and the parts, with `Note over` for the moments between events (dialed but not yet registered; a transaction spanning two passes); `alt/else` for the branch; dashed arrows for stragglers |
| Mid, Low, Principles, Where to look | none by default | a chunk map, a step list, or a table does the job |

If you are about to draw a fourth diagram, ask what table it replaces. If it replaces none, it
is decoration.

## Rules

- Nodes are the same names used in the text: part names on the parts diagram, component and
  process names on the world diagram, function names in a sequence. Never a paraphrase.
- Edge labels are the real transport or the real condition, copied from the code where there is
  one.
- Six participants and fifteen messages is the ceiling for a sequence; split or drop it past that.
- Both themes must stay legible; Mermaid's default theme is fine in Artifacts.

## Backend

Mermaid, in a `<pre class="mermaid">` block. Artifacts render it natively; no library, no CDN.

```html
<pre class="mermaid">
flowchart LR
  subgraph OUT["Outside"]
    C["client program"]
  end
  subgraph SVC["service process"]
    F["<b>focus component</b>"]
    B["bridge"]
  end
  D["downstream (black box)"]
  C -- "protocol / port" --> F
  F --> B
  B -- "topic" --> D
  D -- "reply topic" --> B
</pre>
```

Inline SVG is acceptable for the world diagram when layout carries meaning that Mermaid cannot
express (which thread owns which socket, for example); load the `artifact-diagramming` skill
first. Treat anything else (Excalidraw, external renderers) as an experiment the user opts into.
