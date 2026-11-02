// ── everybody moves: while one fielder chases the ball, the rest go where they would on a real field ──────────────────
// Ground ball in the infield: 1B to the first-base bag (the throw may come there), 2B to the second-base bag in case the runner
// runs on past first, SS (not fielding it) steps in ready for a short throw; if 2B or 1B fields it, SS covers second.
// Ball in the air or to the outfield: the other outfielders run toward the ball to back it up, SS and 2B go out as the cut-off
// men, 1B and 3B take their bags. Everyone leaves after his own reaction time and runs at his own speed.
const STAND = { 1:[62.4, 62.4], 2:[125.9, 0], 3:[62.4, -62.4] };       // [depth, lat] where a fielder stands on a bag, glove up
function planCover(B, c){
  if (!FLD) return;
  FLD.forEach(f => { f.go = null; });
  if (B.hr || (B.foul && !B.isCatch)) return;
  const land = B.pf ? { d:B.pf[0], lat:B.pf[1] } : (B.land || { d:c.tx, lat:c.ty });
  const byPos = p => FLD.find(f => f.pos === p);
  const send = (f, x, y, bag) => { if (f && f !== c && !f.go) f.go = { x, y, bag: bag || 0, dist: Math.hypot(x - f.d, y - f.lat) }; };
  const infield = c.d < 150 && !B.isCatch;
  const toward = (f, t, k) => [f.d + (t.d - f.d) * k, f.lat + (t.lat - f.lat) * k];
  if (infield){
    // 1) the throw is going to a bag: the nearest man who is not fielding it covers that bag
    let covering = null;
    if (B.thr){
      const bags = [[63.64, 63.64], [127.28, 0], [63.64, -63.64]];
      const bi = bags.findIndex(q => Math.abs(q[0] - B.thr.to[0]) < 1 && Math.abs(q[1] - B.thr.to[1]) < 1);
      if (bi >= 0){
        const cand = (bi === 0 ? ['1B', '2B'] : bi === 1 ? ['2B', 'SS'] : ['3B', 'SS']).map(byPos).filter(f => f && f !== c);
        cand.sort((a, b) => Math.hypot(a.d - bags[bi][0], a.lat - bags[bi][1]) - Math.hypot(b.d - bags[bi][0], b.lat - bags[bi][1]));
        if (cand[0]){ covering = cand[0]; send(covering, STAND[bi + 1][0], STAND[bi + 1][1], bi + 1); }
      }
    }
    // 2) the standing assignments
    const first = byPos('1B'), second = byPos('2B'), short = byPos('SS'), third = byPos('3B');
    if (first !== c) send(first, STAND[1][0], STAND[1][1], 1);                                   // 1B to the bag
    if (second !== c) send(second, STAND[2][0], STAND[2][1], 2);                                 // 2B to second, in case the runner goes past first
    if (c === second || c === first) send(short, STAND[2][0] - 3, STAND[2][1] + 3, 2);           // SS covers second when the right side fields it
    else if (short !== c){ const p = toward(short, { d:STAND[2][0], lat:0 }, .5); send(short, p[0], p[1], 0); }   // SS steps in, ready for a short throw
    if (third !== c && third !== covering){ const p = toward(third, land, .25); send(third, p[0], p[1], 0); }
    ['LF', 'CF', 'RF'].forEach(p => { const o = byPos(p); if (o){ const q = toward(o, { d:60, lat:o.lat * .6 }, .22); send(o, q[0], q[1], 0); } });   // outfielders step in to back up
  } else {
    // the ball is in the air or in the outfield
    ['LF', 'CF', 'RF'].forEach(p => { const o = byPos(p); if (o && o !== c){ const q = toward(o, land, .45); send(o, q[0], q[1], 0); } });   // back it up
    const len = Math.hypot(land.d, land.lat) || 1, dir = { d:land.d / len, lat:land.lat / len };
    const cut = { d:Math.min(len * .5, 125) * dir.d, lat:Math.min(len * .5, 125) * dir.lat };
    const second = byPos('2B'), short = byPos('SS');
    const cutMan = land.lat <= 10 ? short : second, other = cutMan === short ? second : short;
    send(cutMan, cut.d, cut.lat, 0);                                                              // the cut-off man lines up with the throw
    send(other, STAND[2][0] - 2, STAND[2][1] + (other === short ? 3 : -2), 2);                    // the other covers second
    send(byPos('1B'), STAND[1][0], STAND[1][1], 1);
    send(byPos('3B'), STAND[3][0], STAND[3][1], 3);
  }
}
