s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:70]); s = s.replace(a, b)

# 1) how many cards turn at once: buy 5 packs = 3 at a time, buy 10 packs = 5 at a time, otherwise one by one
rep("  OPEN = { kind, cards, i:0, t:0, spin:null, revealed:[], n };\n  menu = 'open'; save();",
    "  OPEN = { kind, cards, i:0, t:0, spin:null, revealed:[], n, per: n === 5 ? 3 : n === 10 ? 5 : 1, bspin:null };\n  menu = 'open'; save();")

# 2) revealing and ticking a whole batch: every card spins on its own clock, the better ones turn more times and take longer
rep("function revealNext(){\n  if (!OPEN || OPEN.spin) return;",
"""function spinFor(c){
  const ti = clamp(Math.floor((ovrOf(c) - 60) / 10), 0, 5);
  return { t:0, turns: 4 + ti * 1.2, dur: 1500 - ti * 90 + ti * 260, ti, flash:0 };        // in a batch the great ones also take longer, so they land last
}
function revealNext(){
  if (OPEN && OPEN.per > 1){
    if (OPEN.bspin) return;
    const cs = OPEN.cards.slice(OPEN.i, OPEN.i + OPEN.per); if (!cs.length) return;
    OPEN.bspin = cs.map(c => Object.assign(spinFor(c), { c }));
    return;
  }
  if (!OPEN || OPEN.spin) return;""")
rep("function openTick(dt){\n  if (!OPEN) return;\n  OPEN.t += dt;\n  const sp = OPEN.spin;",
"""function openTick(dt){
  if (!OPEN) return;
  OPEN.t += dt;
  if (OPEN.bspin){
    OPEN.bspin.forEach(b => {
      b.t += dt;
      if (b.t >= b.dur && !b.landed){ b.landed = true; b.flash = 420; G.cards.push(b.c); OPEN.revealed.push(b.c); save(); }
      if (b.landed) b.flash -= dt;
    });
    if (OPEN.bspin.every(b => b.landed) && OPEN.bnext){
      OPEN.bnext = false; OPEN.bspin = null; OPEN.i += OPEN.per; if (OPEN.i >= OPEN.cards.length) OPEN.done = true;
    }
    return;
  }
  const sp = OPEN.spin;""")

# 3) drawing a batch
rep("  if (!OPEN.done) text(`card ${Math.min(OPEN.i + 1, OPEN.cards.length)} of ${OPEN.cards.length}`, cx, 22, UI.ice, 7, 'center');",
    "  if (!OPEN.done) text(OPEN.per > 1 ? `cards ${Math.min(OPEN.i + 1, OPEN.cards.length)}-${Math.min(OPEN.i + OPEN.per, OPEN.cards.length)} of ${OPEN.cards.length}` : `card ${Math.min(OPEN.i + 1, OPEN.cards.length)} of ${OPEN.cards.length}`, cx, 22, UI.ice, 7, 'center');")
rep("  const w = 76, h = 107;\n  if (!sp){",
"""  if (OPEN.per > 1){
    const cnt = Math.min(OPEN.per, OPEN.cards.length - OPEN.i), bw = OPEN.per === 3 ? 62 : 46, bh = Math.round(bw * 1.4), gp = OPEN.per === 3 ? 10 : 6;
    const x0 = cx - (cnt * bw + (cnt - 1) * gp) / 2, y0 = cy - bh / 2, bs = OPEN.bspin;
    if (!bs){
      // face-down cards (the pack itself for the first batch), tap to turn them all over
      const bob = Math.sin(OPEN.t / 300) * 3; rays(.3, '255,255,255');
      for (let k = 0; k < cnt; k++){
        const x = x0 + k * (bw + gp);
        uiBox(x, y0 + bob, bw, bh, mix(UI.blueDD, P2.col, .35)); g.fillStyle = P2.col2; g.beginPath(); g.arc(x + bw / 2, cy + bob, 9, 0, 7); g.fill();
        g.fillStyle = UI.navy; g.fillRect(x + bw / 2 - 9, cy + bob - 1, 18, 2);
      }
      const pulse = .6 + .4 * Math.sin(OPEN.t / 220);
      ptitle(OPEN.i === 0 ? 'TAP TO OPEN' : 'TAP TO REVEAL', cx, y0 + bh + 12, 9, `rgba(255,255,255,${.7 + .3 * pulse})`);
      btns.push({ x:0, y:30, w:W, h:H - 30, fn: revealNext });
      return;
    }
    const top = bs.reduce((m, b) => b.ti > m.ti ? b : m, bs[0]), rgbT = top.ti >= 5 ? '255,77,77' : top.ti >= 4 ? '255,210,63' : top.ti >= 3 ? '178,107,255' : '255,255,255';
    rays(bs.every(b => b.landed) ? 1 : clamp(top.t / top.dur, 0, 1) * (top.ti + 1) / 6, rgbT);
    bs.forEach((b, k) => {
      const x = x0 + k * (bw + gp), mx = x + bw / 2, f = clamp(b.t / b.dur, 0, 1), eased = 1 - Math.pow(1 - f, 2.1), ang = eased * b.turns * Math.PI, sx = Math.abs(Math.cos(ang)), tcol = TIERS[b.ti].col;
      if (b.landed){
        drawCard(x, y0, b.c, bw, bh, OPEN.t);
        const fl = clamp(b.flash / 420, 0, 1); if (fl > 0) R(x - 3, y0 - 3, bw + 6, bh + 6, `rgba(255,255,255,${fl * .55})`);
        if (b.ti >= 2) ptitle(TIER_LABEL[b.ti], mx, y0 - 14, b.ti >= 4 ? 8 : 7, tcol);
      } else {
        const face = Math.cos(ang) > 0, cw2 = Math.max(2, Math.round(bw * sx));
        if (face){ g.save(); g.translate(mx, 0); g.scale(sx, 1); g.translate(-mx, 0); drawCard(x, y0, b.c, bw, bh, OPEN.t); g.restore(); }
        else { R(mx - cw2 / 2, y0, cw2, bh, mix(UI.blueDD, tcol, .45)); g.strokeStyle = '#fff'; g.strokeRect(mx - cw2 / 2 + .5, y0 + .5, cw2 - 1, bh - 1); }
        if (b.ti >= 3){ const gl = f * (b.ti - 2) / 3; for (let i = 4; i > 0; i--) R(x - i * 2, y0 - i * 2, bw + i * 4, bh + i * 4, `rgba(${rgbT},${.05 * gl})`); }
      }
    });
    if (bs.every(b => b.landed)){
      const ready = bs.every(b => b.flash < 260);
      if (bs.every(b => b.flash <= 0)) ptitle('TAP', cx, y0 + bh + 12, 8, UI.ice);
      btns.push({ x:0, y:0, w:W, h:H, fn: () => { if (ready) OPEN.bnext = true; } });
    }
    return;
  }
  const w = 76, h = 107;
  if (!sp){""")
s = s.replace("BUILD = '11-03n'", "BUILD = '11-03o'")
open('index.html', 'w', encoding='utf-8').write(s)
import re
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
