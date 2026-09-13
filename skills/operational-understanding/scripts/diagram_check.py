#!/usr/bin/env python3
"""Layout check for the drill-down template's deterministic diagrams.

Extracts renderArch/renderSeq from the page, runs them over every JSON spec, and fails if any
text lands outside the viewBox, any node label line exceeds the node width, or any edge's
vertical segment passes through a node box (returns must use the gutters). Also fails if the
page's main <script> block contains a literal </script>. Requires node on PATH.
"""
import json, re, subprocess, sys, tempfile

def main() -> int:
    s = open(sys.argv[1], encoding="utf-8").read()
    js = s[s.rindex("<script>") + 8 : s.rindex("</script>")]
    if re.search(r"</\s*script", js, re.I):
        print("FAIL: literal </script> inside the main script block"); return 1
    head = js[js.index("  const PART_FILL =") : js.index("  // a diagset:")]
    specs = [json.loads(m) for m in re.findall(r'<script type="application/json">(.*?)</script>', s, re.S)]
    test = head + """
const specs = %s; let bad = 0, n = 0;
for (const set of specs) for (const sp of set) { const svg = sp.type === 'seq' ? renderSeq(sp) : renderArch(sp); n++;
  const vb = svg.match(/viewBox="0 0 ([\\d.]+) ([\\d.]+)"/).slice(1).map(Number);
  for (const m of svg.matchAll(/<text[^>]*x="([\\d.-]+)"[^>]*y="([\\d.-]+)"/g)) { const x=+m[1], y=+m[2]; if (x < 0 || x > vb[0] || y < 0 || y > vb[1]) { bad++; console.log('OUT', sp.title, x, y); } }
  if (sp.type !== 'seq') for (const nd of sp.nodes) for (const l of nd.lines) if (l.length > 26) { bad++; console.log('NODE-OVERFLOW', sp.title, l); }
  if (sp.type !== 'seq') { const rects=[...svg.matchAll(/<rect class="dg-node" x="([\\d.]+)" y="([\\d.]+)" width="([\\d.]+)" height="([\\d.]+)"/g)].map(m=>m.slice(1).map(Number));
    for (const m of svg.matchAll(/<path class="dg-edge[^"]*" d="([^"]+)"/g)) { const cmds=[...m[1].matchAll(/([MHV])([\\d.-]+)(?:,([\\d.-]+))?/g)]; let x=0,y=0; for (const c of cmds) { if (c[1]==='M'){x=+c[2];y=+c[3];} else if (c[1]==='H'){x=+c[2];} else { const y2=+c[2]; for (const [rx,ry,rw,rh] of rects) { if (x>rx+1 && x<rx+rw-1 && Math.min(y,y2)<ry+rh-1 && Math.max(y,y2)>ry+1) { bad++; console.log('THROUGH-NODE', sp.title); } } y=y2; } } } }
}

for (const set of specs) for (const sp of set) if (sp.type !== 'seq') { const svg = renderArch(sp); const segs=[];
  for (const m of svg.matchAll(/<path class="dg-edge[^"]*" d="([^"]+)"/g)) { const cmds=[...m[1].matchAll(/([MHV])([\\d.-]+)(?:,([\\d.-]+))?/g)]; let x=0,y=0; for (const c of cmds) { if (c[1]==='M'){x=+c[2];y=+c[3];} else if (c[1]==='H'){x=+c[2];} else { segs.push([x, Math.min(y,+c[2]), Math.max(y,+c[2]), m[1]]); y=+c[2]; } } }
  for (let i=0;i<segs.length;i++) for (let j=i+1;j<segs.length;j++) { const [x1,a1,b1,p1]=segs[i],[x2,a2,b2,p2]=segs[j]; if (p1!==p2 && Math.abs(x1-x2)<3 && Math.min(b1,b2)-Math.max(a1,a2)>4) { bad++; console.log('COINCIDENT-VERTICAL', sp.title, x1); } } }
for (const set of specs) for (const sp of set) if (sp.type !== 'seq') { const svg = renderArch(sp); const H=[], V=[];
  for (const m of svg.matchAll(/<path class="(dg-edge[^"]*)" d="([^"]+)"/g)) { const solid = !m[1].includes('dg-ret'); const cmds=[...m[2].matchAll(/([MHV])([\\d.-]+)(?:,([\\d.-]+))?/g)]; let x=0,y=0; for (const c of cmds) { if (c[1]==='M'){x=+c[2];y=+c[3];} else if (c[1]==='H'){ H.push([Math.min(x,+c[2]),Math.max(x,+c[2]),y,m[2],solid]); x=+c[2]; } else { V.push([x,Math.min(y,+c[2]),Math.max(y,+c[2]),m[2],solid]); y=+c[2]; } } }
  for (const [hx1,hx2,hy,hp,hs] of H) for (const [vx,vy1,vy2,vp,vs] of V) if (hp!==vp && hs && vs && vx>hx1+2 && vx<hx2-2 && hy>vy1+2 && hy<vy2-2) { bad++; console.log('SOLID-CROSSING', sp.title, 'at', vx, hy); } }
console.log('diagrams', n, 'problems', bad); process.exit(bad ? 1 : 0);
""" % json.dumps(specs)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(test); path = f.name
    return subprocess.call(["node", path])

if __name__ == "__main__":
    sys.exit(main())
