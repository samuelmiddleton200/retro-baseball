import re
g = open('gl3d.js', encoding='utf-8').read()
x = open('index.html', encoding='utf-8').read()
def rep(s, a, b, cnt=1):
    assert s.count(a) == cnt, (s.count(a), a[:80]); return s.replace(a, b)

# ── 1) the hit camera: a second-deck press box, 100 ft up and 70 ft back, home plate in sight ──
g = rep(g, "  else { c.fov = 60; c.up.set(0, 1, 0); c.position.set(0, 100, 50); c.lookAt(0, 0, -112); }          // the press box: 100 ft up, 50 ft behind the plate",
           "  else { c.fov = 58; c.up.set(0, 1, 0); c.position.set(0, 100, 70); c.lookAt(0, 0, -70); }          // a second-deck press box: 100 ft up, 70 ft back; home plate stays in view")

# ── 2) the grass: parallel straight stripes 5.25 ft wide, one centred on the line home - mound - second base; the infield uses the same stripes ──
g = rep(g, """  // base grass, with wide mowing stripes running out from home
  g.fillStyle = GRASS_A; g.fillRect(0, 0, reg.w, reg.h);
  for (let i = -24; i < 24; i++){
    if (i % 2) continue;
    poly([[i * 14, D0], [i * 14 + 14, D0], [i * 14 + 14, D0 + DW], [i * 14, D0 + DW]], GRASS_B);
  }
""", """  // mowing: parallel straight stripes, 5.25 ft wide, light and dark the same width. One is centred on the line home - mound - second base, and the infield uses the very same
  // stripes (they are laid down by world position), so every infield stripe carries straight on into the outfield.
  const MOW_W = 5.25;
  const mow = () => {
    g.fillStyle = GRASS_C; g.fillRect(0, 0, reg.w, reg.h);
    for (let i = -70; i <= 70; i += 2){ const x0 = P((i - .5) * MOW_W, 0)[0], x1 = P((i + .5) * MOW_W, 0)[0]; g.fillStyle = GRASS_B; g.fillRect(x0, 0, x1 - x0, reg.h); }
  };
  mow();
""")
a = g.index("  // diagonal stripes inside the infield diamond"); b = g.index("  // the dirt edge: a strip of dirt exactly 20 ft wide")
g = g[:a] + g[b:]
a = g.index("  poly(GD, GRASS_A);"); b = g.index("  circ(0, 0, 17, DIRT2);")
g = g[:a] + "  g.save(); g.beginPath(); GD.forEach((p, i) => { const q = P(p[0], p[1]); i ? g.lineTo(q[0], q[1]) : g.moveTo(q[0], q[1]); }); g.closePath(); g.clip(); mow(); g.restore();\n" + g[b:]
g = rep(g, "t.anisotropy = 4;", "t.anisotropy = 16;")                       # the far stripes stay sharp all the way to the wall

# ── 3) chalk: straight rectangles, a bit thicker; the pitching rubber is a neat white rectangle on the mound ──
g = rep(g, "g.lineWidth = .5 * S; g.strokeRect(a[0], a[1], b[0] - a[0], b[1] - a[1]); };", "g.lineWidth = .7 * S; g.lineJoin = 'miter'; g.strokeRect(a[0], a[1], b[0] - a[0], b[1] - a[1]); };")
g = rep(g, "  circ(0, 0, 17, DIRT2); circ(0, 60.5, 9.5, DIRT2);",
           "  circ(0, 0, 17, DIRT2); circ(0, 60.5, 9.5, DIRT2);\n  { const A = P(-1.9, 61.0), B = P(1.9, 60.0); g.fillStyle = '#f6f3ea'; g.fillRect(A[0], A[1], B[0] - A[0], B[1] - A[1]); g.strokeStyle = '#6b4a2a'; g.lineWidth = .18 * S; g.strokeRect(A[0], A[1], B[0] - A[0], B[1] - A[1]); }      // the pitching rubber")

# ── 4) the crowd: about 42,500 little 3D people (head + body) facing the field, 60/20/15/5 in the clubs' colours ──
old = """  strip([[1.5, wallH + .2], [50, wallH + 26]], crowdMat, 96, 12);                       // the lower deck: 50 ft deep behind the fence
  strip([[50, wallH + 26], [50, wallH + 30]], basic(0x203a40), 1, 1);                   // the rail between the decks
  strip([[50, wallH + 30], [100, wallH + 60]], crowdMat, 96, 12);                       // the upper deck: another 50 ft
"""
new = """  // the stands are plain dark slopes; the crowd is thousands of little people standing on them (below)
  strip([[1.5, wallH + .2], [50, wallH + 26]], basic(0x1e242e), 1, 1);                  // the lower deck: 50 ft deep behind the fence
  strip([[50, wallH + 26], [50, wallH + 30]], basic(0x203a40), 1, 1);                   // the rail between the decks
  strip([[50, wallH + 30], [100, wallH + 60]], basic(0x1e242e), 1, 1);                  // the upper deck: another 50 ft
  {
    const C4 = teamCols.length >= 4 ? teamCols : [teamCols[0], teamCols[1], '#ffffff', '#222222'];     // home main, home secondary, away main, away secondary
    const FANS = 42500, SC = .75, ROWS = 16;
    const rowsInfo = []; [[1.5, 50, wallH + .2, wallH + 26], [50, 100, wallH + 30, wallH + 60]].forEach(([r0, r1, y0, y1]) => { for (let i = 0; i < ROWS; i++){ const u = (i + .5) / ROWS; rowsInfo.push([r0 + (r1 - r0) * u, y0 + (y1 - y0) * u]); } });
    const at2 = a => { const t = a * D2R, r = fenceR(park, a); return [Math.sin(t) * r, -Math.cos(t) * r]; };
    const path = []; for (let a = -180; a <= 180; a += .5){ const p = at2(a), p0 = at2(a - .5), p1 = at2(a + .5); let tx = p1[0] - p0[0], tz = p1[1] - p0[1]; const tl = Math.hypot(tx, tz) || 1; tx /= tl; tz /= tl;
      let nx = tz, nz = -tx; if (nx * p[0] + nz * p[1] < 0){ nx = -nx; nz = -nz; } path.push([p[0], p[1], nx, nz]); }
    let seats; const gen = gap => { seats = []; rowsInfo.forEach(([r, y]) => { let acc = 0, last = path[0]; for (let k = 1; k < path.length; k++){ const q = path[k]; const seg = Math.hypot(q[0] - last[0], q[1] - last[1]); acc += seg;
      while (acc >= gap){ acc -= gap; const u = 1 - acc / (seg || 1); seats.push([last[0] + (q[0] - last[0]) * u + (last[2] + (q[2] - last[2]) * u) * r, y, last[1] + (q[1] - last[1]) * u + (last[3] + (q[3] - last[3]) * u) * r, q[2], q[3]]); } last = q; } }); };
    let gap = 1.7; gen(gap); gap = gap * seats.length / FANS; gen(gap);                      // spaced so there are about 42,500 of them
    const boxG = (w, h, d, y) => { const bg = new THREE.BoxGeometry(w, h, d); bg.translate(0, y, 0); const n = bg.attributes.normal, cols = []; for (let i = 0; i < n.count; i++){ const ny = n.getY(i), nxx = Math.abs(n.getX(i)), nzz = n.getZ(i); const k = ny > .5 ? 1 : ny < -.5 ? .45 : nzz > .5 ? .88 : nxx > .5 ? .66 : .55; cols.push(k, k, k); } bg.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3)); return bg; };
    const fm = new THREE.MeshBasicMaterial({ vertexColors: true });
    const n = seats.length, body = new THREE.InstancedMesh(boxG(1.25 * SC, 1.5 * SC, .8 * SC, .75 * SC), fm, n), head = new THREE.InstancedMesh(boxG(.62 * SC, .66 * SC, .62 * SC, .33 * SC), fm, n);
    const hx = h => { const c = new THREE.Color(h); return [c.r, c.g, c.b]; };
    const SK = ['#f1c9a0', '#d9a577', '#b57d52', '#8a5a38', '#6b4430'].map(hx), TEAM = C4.map(hx);
    const D = new THREE.Object3D(), col = new THREE.Color();
    seats.forEach((s, i) => {
      const r = rr(), ti = r < .6 ? 0 : r < .8 ? 1 : r < .95 ? 2 : 3, j = .82 + rr() * .36;
      const yaw = Math.atan2(-s[3], -s[4]) + (rr() - .5) * .5, jx = (rr() - .5) * .35, jz = (rr() - .5) * .5;
      D.position.set(s[0] + jx, s[1], s[2] + jz); D.rotation.set(0, yaw, 0); D.scale.set(1, 1, 1); D.updateMatrix(); body.setMatrixAt(i, D.matrix);
      col.setRGB(Math.min(1, TEAM[ti][0] * j), Math.min(1, TEAM[ti][1] * j), Math.min(1, TEAM[ti][2] * j)); body.setColorAt(i, col);
      D.position.set(s[0] + jx, s[1] + 1.5 * SC - .1 * SC, s[2] + jz); D.updateMatrix(); head.setMatrixAt(i, D.matrix);
      const sk = SK[(rr() * SK.length) | 0]; col.setRGB(sk[0], sk[1], sk[2]); head.setColorAt(i, col);
    });
    [body, head].forEach(m => { m.instanceMatrix.needsUpdate = true; m.instanceColor.needsUpdate = true; m.frustumCulled = false; G.add(m); });
    GL.fanCount = n;
  }
"""
g = rep(g, old, new)
open('gl3d.js', 'w', encoding='utf-8').write(g)

# the park's colours: home main, home secondary, away main, away secondary
x = rep(x, "parkKey: 'p' + (M.park.wall || '') + M.park.cf, parkCols: [uni(ft), uni(bt)],", "parkKey: 'p' + (M.park.wall || '') + M.park.cf, parkCols: [uni(M.home), uni2(M.home), uni(M.away), uni2(M.away)],")
x = re.sub(r"gl3d\.js\?v=11-05[a-z]", "gl3d.js?v=11-06a", x)
x = x.replace("BUILD = '11-05u'", "BUILD = '11-06a'")
open('index.html', 'w', encoding='utf-8').write(x)
print('ok')
