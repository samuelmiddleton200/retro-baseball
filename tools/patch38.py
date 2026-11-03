s = open('index.html', encoding='utf-8').read()

def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)

# ── 1) FLD is the arm AND the legs: speed rating = fielding rating; throw 70 mph at 60 up to 100 mph at 120; range 200 ft up to 400 ft ──
rep("  ARM_BASE: 60, ARM_SLOPE: 0.5, // throw mph = 60 + (rating - 60) * 0.5", "  ARM_BASE: 70, ARM_SLOPE: 0.5, // throw mph = 70 + (fielding - 60) * 0.5: 60 throws 70 mph, 120 throws 100 mph\n  ARM_RANGE0: 200, ARM_RANGE_SLOPE: 200 / 60,   // furthest a man can throw it: 200 ft at 60 fielding, 400 ft at 120")
rep("  THROW_EFFICIENCY: 0.93,       // average speed of a throw vs its release speed (drag)", "  THROW_EFFICIENCY: 1.0,        // the stated throwing speeds are what the ball does")
rep("const throwFps = r =>", """const throwRange = r => CFG.ARM_RANGE0 + (r - 60) * CFG.ARM_RANGE_SLOPE;           // feet
const spdOf = m => (m && (m.fielding != null ? m.fielding : m.speed)) || 70;       // a hitter runs with his FIELDING rating
const throwFps = r =>""")
for item in [
    ("sprintFps(man.speed)", "sprintFps(spdOf(man))", 2), ("runTime(man.speed, c.pos - s0)", "runTime(spdOf(man), c.pos - s0)"),
    ("runDist(man.speed, c.te - CFG.RUN_START_DELAY) < c.cap", "runDist(spdOf(man), c.te - CFG.RUN_START_DELAY) < c.cap"),
    ("c.pos = Math.min(c.cap, s0 + runDist(man.speed,", "c.pos = Math.min(c.cap, s0 + runDist(spdOf(man),"),
    ("runTime(c.man.speed, c.pos - c.s0)", "runTime(spdOf(c.man), c.pos - c.s0)"),
    ("const b = M.batter, spd = b.speed, tf = B.tf", "const b = M.batter, spd = spdOf(b), tf = B.tf"),
    ("r1 = runTime(M.bases[0].speed, 90)", "r1 = runTime(spdOf(M.bases[0]), 90)"),
    ("(r1.speed - 85) / 300", "(spdOf(r1) - 85) / 300"), ("(r2.speed - 85) / 300", "(spdOf(r2) - 85) / 300"),
    ("GL3D.poseRun(mv.ph, man.speed)", "GL3D.poseRun(mv.ph, spdOf(man))"),
    ("runDist(M.batter.speed, B.t - CFG.RUN_START_DELAY)", "runDist(spdOf(M.batter), B.t - CFG.RUN_START_DELAY)"),
    ("runDist(p2.speed, B.t - CFG.RUN_START_DELAY)", "runDist(spdOf(p2), B.t - CFG.RUN_START_DELAY)"),
    ("spd = (b.speed - 85) / 30", "spd = (spdOf(b) - 85) / 30"),
]:
    rep(*item)

# the SPD number on a card follows FLD (new cards, saves, upgrades)
rep("  p.ovr = Math.round((p.contact + p.power + p.speed + p.fielding) / 4);\n  p.st = newStat();", "  p.speed = p.fielding;                                              // his speed IS his fielding rating\n  p.ovr = Math.round((p.contact + p.power + p.speed + p.fielding) / 4);\n  p.st = newStat();")
rep("      G.cards.forEach(c => { c.st = c.st || newStat(); });", "      G.cards.forEach(c => { c.st = c.st || newStat(); if (c.fielding != null) c.speed = c.fielding; });")
rep("  keys.forEach(k => c[k] = clamp(c[k] + d, 60, 120));\n  c.id = _cardId++;", """  if (c.fielding != null){                                    // a hitter: speed follows fielding, so the three real stats carry the shift
    const k3 = ['contact', 'power', 'fielding'];
    for (let n = 0; n < 6; n++){ c.speed = c.fielding; const dd = lvl - ovrOf(c); if (!dd) break; k3.forEach(k => c[k] = clamp(c[k] + dd, 60, 120)); }
    c.speed = c.fielding;
  } else keys.forEach(k => c[k] = clamp(c[k] + d, 60, 120));
  c.id = _cardId++;""")
rep("      G.coins -= cost; c[statsOf(c)[upStat][1]] = clamp(c[statsOf(c)[upStat][1]] + 2, 60, 120);", "      G.coins -= cost; { const sk = statsOf(c)[upStat][1] === 'speed' ? 'fielding' : statsOf(c)[upStat][1]; c[sk] = clamp(c[sk] + 2, 60, 120); if (c.fielding != null) c.speed = c.fielding; }")

# ── 2) throw routes: a man can only throw so far; beyond that it goes to an infielder who throws it on ──
rep("// where the ball is at time t: on its flight, in a fielder's hands, or on a throw\nfunction ballPos(B, t){", '''const RELAY_TR = 0.55;                                     // an infielder catching it and throwing it on
const BASE_PTS4 = [[63.64, 63.64], [127.28, 0], [63.64, -63.64], [0, 0]];
// The quickest way to get the ball from `from` to `tgt`. Straight there if he can reach (his range), otherwise through one or two infielders
// (centre field to second, then home; right field to short or first, then third). Every leg is a throw at that man's own speed and range.
// live: the fielders are where they are now (a play in progress); otherwise it is the plan made as the ball is hit.
function routeThrow(thrower, from, t0, tgt, tr, live){
  const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
  const mates = (FLD || []).filter(f => f !== thrower && ['1B', '2B', 'SS', '3B'].includes(f.pos));
  let best = null;
  const leg = (a, b, ts, fps) => { const len = dist(a, b); return { from:a, to:b, t0:ts, t1:ts + len / fps, len }; };
  const walk = (cur, rng, fps, tRel, legs, used, relays) => {
    if (dist(cur, tgt) <= rng){
      const L = legs.concat([leg(cur, tgt, tRel, fps)]);
      if (!best || L[L.length - 1].t1 < best.arr) best = { legs:L, arr:L[L.length - 1].t1, relays };
    }
    if (used.length >= 2) return;
    for (const m of mates){
      if (used.includes(m)) continue;
      const d0 = dist(cur, tgt), mr = throwRange(m.man.fielding), spots = [live ? [m.x, m.y] : [m.d, m.lat]];
      for (const fr of [.5, .65, .8, .9, .98]){ const along = Math.min(rng * fr, d0 * .85), u = d0 > 0 ? along / d0 : 0; spots.push([cur[0] + (tgt[0] - cur[0]) * u, cur[1] + (tgt[1] - cur[1]) * u]); }
      for (const sp of spots){
        if (dist(cur, sp) > rng || (dist(sp, tgt) > mr && used.length >= 1) || dist(sp, tgt) >= d0 - 8) continue;
        const l1 = leg(cur, sp, tRel, fps);
        const reach = live ? BALL.t + dist([m.x, m.y], sp) / (m.speed * CFG.ROUTE_EFF) : fldReach(m, dist([m.d, m.lat], sp));
        if (reach > l1.t1) continue;                                          // he cannot get there before the ball does
        walk(sp, mr, m.armFps, l1.t1 + RELAY_TR, legs.concat([l1]), used.concat([m]), relays.concat([{ f:m, spot:sp }]));
      }
    }
  };
  walk(from, throwRange(thrower.man.fielding), thrower.armFps, t0 + tr, [], [], []);
  if (!best){ const l = leg(from, tgt, t0 + tr, thrower.armFps); best = { legs:[l], arr:l.t1, relays:[] }; }
  return best;
}
const mkThr = (rt, from, to) => ({ t0: rt.legs[0].t0, t1: rt.legs[rt.legs.length - 1].t1, from, to, len: rt.legs.reduce((a, l) => a + l.len, 0), legs: rt.legs, relays: rt.relays });
// where the ball is on a throw made of legs: flying along one, or waiting in the hands of the man who throws it on
function thrPos(thr, t){
  const L = thr.legs;
  for (const l of L){
    if (t < l.t0) return { d:l.from[0], lat:l.from[1], flying:false, u:0, len:l.len };
    if (t <= l.t1){ const u = clamp((t - l.t0) / Math.max(.05, l.t1 - l.t0), 0, 1); return { d:lerp(l.from[0], l.to[0], u), lat:lerp(l.from[1], l.to[1], u), flying:true, u, len:l.len }; }
  }
  const l = L[L.length - 1]; return { d:l.to[0], lat:l.to[1], flying:false, u:1, len:l.len };
}
// where the ball is at time t: on its flight, in a fielder's hands, or on a throw
function ballPos(B, t){''')
rep("""    if (B.thr && t >= B.thr.t0){
      const u = clamp((t - B.thr.t0) / (B.thr.t1 - B.thr.t0), 0, 1);
      return { d: lerp(B.thr.from[0], B.thr.to[0], u), lat: lerp(B.thr.from[1], B.thr.to[1], u), h: 4 + 5 * Math.sin(Math.PI * u) * Math.min(1, B.thr.len / 120) };
    }""", """    if (B.thr && t >= B.thr.t0){
      const tp = thrPos(B.thr, t);
      return { d: tp.d, lat: tp.lat, h: tp.flying ? 4 + 5 * Math.sin(Math.PI * tp.u) * Math.min(1, tp.len / 120) : 4 };
    }""")
rep("""    if (B.t < B.thr.t1) B.inFlightThrow = true; else B.heldAfter = true;                     // the planned throw (a ground out, a single): the ball flies to the base and stays there
    const u = clamp((B.t - B.thr.t0) / Math.max(.05, B.thr.t1 - B.thr.t0), 0, 1);
    B.d = lerp(B.thr.from[0], B.thr.to[0], u); B.lat = lerp(B.thr.from[1], B.thr.to[1], u); B.h = 4 + Math.sin(u * Math.PI) * Math.min(16, B.thr.len * .09);""",
"""    const tp = thrPos(B.thr, B.t);                                                           // the planned throw (a ground out, a single): the ball flies leg by leg and stays at the base
    if (tp.flying) B.inFlightThrow = true; else B.heldAfter = true;
    B.d = tp.d; B.lat = tp.lat; B.h = tp.flying ? 4 + Math.sin(tp.u * Math.PI) * Math.min(16, tp.len * .09) : 4;""")
rep("if (B.pass){ if (B.pass.ph === 'fly') B.inFlightThrow = true; else B.heldAfter = true; } }", "if (B.pass){ if (B.pass.ph === 'fly' && B.pass.fl) B.inFlightThrow = true; else B.heldAfter = true; } }")

# manual play: the man holding it throws it on through relays too
rep("""    const to = BASE_XY[best.bi], len = Math.hypot(to[0] - P.x, to[1] - P.y);
    B.pass = { ph:'fly', fr:[P.x, P.y], to, len, t0:B.t, t1:B.t + len / T.arm, run:best };
    return;""", """    const to = BASE_XY[best.bi];
    const holder = P.first ? B.chaser : (FLD || []).reduce((a, f) => Math.hypot(f.x - P.x, f.y - P.y) < Math.hypot(a.x - P.x, a.y - P.y) ? f : a);
    const rt = routeThrow(holder, [P.x, P.y], B.t, to, 0, true), thr = mkThr(rt, [P.x, P.y], to);
    B.pass = { ph:'fly', thr, to, t1:thr.t1, run:best, fl:true };
    return;""")
rep("B.pass = { ph:'hold', x:T.pf[0], y:T.pf[1], t0:B.t }; }", "B.pass = { ph:'hold', x:T.pf[0], y:T.pf[1], t0:B.t, first:true }; }")
rep("""  const u = clamp((B.t - P.t0) / Math.max(.05, P.t1 - P.t0), 0, 1);
  B.d = lerp(P.fr[0], P.to[0], u); B.lat = lerp(P.fr[1], P.to[1], u); B.h = 4 + Math.sin(u * Math.PI) * Math.min(16, P.len * .09);
  if (B.t >= P.t1){""", """  const tp = thrPos(P.thr, B.t); P.fl = tp.flying;
  B.d = tp.d; B.lat = tp.lat; B.h = tp.flying ? 4 + Math.sin(tp.u * Math.PI) * Math.min(16, tp.len * .09) : 4;
  if (B.t >= P.t1){""")

# ── 3) the plan made as the ball is hit: arrival times come from the routes ──
rep("""  const baseDist = n => Math.hypot(pf[0] - bases[n - 1][0], pf[1] - bases[n - 1][1]);
  const throwArr = (n, tr) => tf + tr + baseDist(n) / c.armFps;
  const throwTo = (n, tr) => { B.thr = { t0: tf + tr, t1: throwArr(n, tr), from: pf, to: bases[n - 1], len: baseDist(n) }; };""",
"""  const baseDist = n => Math.hypot(pf[0] - bases[n - 1][0], pf[1] - bases[n - 1][1]);
  const routes = {}, route = (n, tr) => routes[n + '|' + tr] || (routes[n + '|' + tr] = routeThrow(c, pf, tf, bases[n - 1], tr, false));
  const throwArr = (n, tr) => route(n, tr).arr;
  const throwTo = (n, tr) => { B.thr = mkThr(route(n, tr), pf, bases[n - 1]); };""")
rep("      if (a2 < r1){ const a1b = a2 + .55 + 127.28 / (c.armFps * .9);", "      if (a2 < r1){ const a1b = a2 + .55 + 127.28 / (c.armFps * .9);")
# the relay men go where the throw needs them
rep("function planCover(B, c){\n  if (!FLD) return;\n  FLD.forEach(f => { f.go = null; });", "function planCover(B, c){\n  if (!FLD) return;\n  FLD.forEach(f => { f.go = null; f.relay = false; });")
i = s.index("function planCover(B, c){")
j = s.index("\n}\n", i)
s = s[:j] + "\n  if (B.thr && B.thr.relays) B.thr.relays.forEach(r => { r.f.go = { x:r.spot[0], y:r.spot[1], bag:0, dist:Math.hypot(r.spot[0] - r.f.d, r.spot[1] - r.f.lat) }; r.f.relay = true; });      // a relay man stands where the long throw will find him" + s[j:]
s = s.replace("BUILD = '11-03y'", "BUILD = '11-03z'")
# hooks for tests
rep("runToggle, runBack, drawPlay, skinHex,", "runToggle, runBack, drawPlay, throwRange, throwFps, spdOf, routeThrow, skinHex,")
open('index.html', 'w', encoding='utf-8').write(s)
import re
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
