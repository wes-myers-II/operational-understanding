# Diagram guide

Pick the diagram by what the reader must *see*, not by what is easiest to draw. Each diagram
gets a one-line caption: "Notice: …".

## Selection

| Reader must see | Use | Level |
|---|---|---|
| who talks to whom — processes, threads, sockets, queues, services | architecture (inline SVG; Mermaid `flowchart LR` for drafts) | High |
| one interaction end to end across parties, in time | Mermaid `sequenceDiagram` | High (one), Mid (per scenario) |
| a lifecycle: states and what moves between them | Mermaid `stateDiagram-v2` | Mid |
| decision logic with real conditions | Mermaid `flowchart TD`, condition text on edges | Mid / Low |
| a data structure and what indexes it | small inline SVG or a table | Low |
| a timeline with a gap or race | `sequenceDiagram` with `Note over` for the gap, or a two-column table | Mid / Low |

Sequence diagrams are the workhorse for anything with a handshake, handoff, or request/reply.
State diagrams earn their place only when the states are named in code (flags, enums). Use
tables instead of diagrams when a diagram would just be a table with arrows.

## Backends

**Mermaid (default).** Renders natively in Artifacts:

```html
<pre class="mermaid">
sequenceDiagram
  participant C as Client
  participant S as Service (ConnectionManager)
  C->>S: hello on discovery port
  S->>C: open data channels back to client
  Note over C,S: Stage A — connected at transport, not yet registered
  C->>S: first request
  S->>S: ResolveSender → sessions[conn_id] = Primary
</pre>
```

No library, no CDN. Keep participants ≤ 6 and messages ≤ 15 per diagram; split otherwise.

**Inline SVG (architecture).** Load the `artifact-diagramming` skill first. Use for boxes-and-
wires where layout carries meaning (which thread owns which socket or queue, which side
initiates a connection).
Both themes must remain legible; that skill covers the mechanics.

**Experimental: Excalidraw.** Not installed as a skill here. Two possible paths if the user
wants to try it: (a) author `.excalidraw` JSON and embed the `@excalidraw/excalidraw` UMD from
`https://cdn.jsdelivr.net/npm/` (allowed CDN) to render it read-only inside the artifact —
heavy, unverified, expect a session of fiddling; (b) draw in the Excalidraw app, export SVG,
inline it as a data: URI. (b) is reliable but manual. Treat either as an experiment the user
opts into, not a default.

## Patterns that worked

- **The gap**: when "connected" or "complete" has two stages, draw the sequence with an explicit
  `Note over` between them naming the state during the gap. This single device prevented the
  most misunderstandings.
- **Both branches**: for a dial/attempt that can fail, draw success and failure as `alt`/`else`
  in one sequence rather than two diagrams.
- **State table beats state diagram** when fewer than four states or when the interesting part
  is *which fields* change, not *which state* you're in.
- **Ghost / straggler messages**: show them as a dashed arrow (`-->>`) with the discard as a
  `Note`.

## Mermaid snippets

Lifecycle:
```
stateDiagram-v2
  [*] --> Listening: no client
  Listening --> ConnectedUnregistered: client connects / reconnect to known peer
  ConnectedUnregistered --> Registered: first request → sessions[conn_id]
  Registered --> Listening: explicit disconnect | heartbeat timeout
```

Decision with real conditions (copy the condition text from the code):
```
flowchart TD
  A[new connection id] --> B{sessions empty?}
  B -- yes --> M[role = Primary]
  B -- no --> C{one session && secondary_invited?}
  C -- yes --> X[role = Secondary]
  C -- no --> R[drain payload; return -1; no reply]
```
