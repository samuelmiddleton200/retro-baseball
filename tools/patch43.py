s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── fastballs: 60 velocity = 82 mph, 120 = 106 mph ──
rep("FB_BASE: 70, FB_SLOPE: 0.58,  // fastball mph = 70 + (rating - 60) * 0.58", "FB_BASE: 82, FB_SLOPE: 0.4,   // fastball mph = 82 + (rating - 60) * 0.4: 60 throws 82, 120 throws 106")

# ── tiredness: a pitcher's pitch count in THIS game against his limit (60 stamina = 60 pitches, 120 = 100) ──
rep("""function fatigue(){
  const p = curPitcher(), pc = M.top ? M.pcHome : M.pcAway;
  const cap = 40 + (p.stamina - 60) * 1.6;              // ~40 pitches at 60 stamina, ~135 at 120
  return clamp(pc / cap, 0, 1.8);
}""", """// what each pitcher has done in this game: pitches, runs, outs, and whether he has been in (a pitcher taken out cannot come back)
const PG = new Map();
const pg = p => PG.get(p) || (PG.set(p, { pc:0, r:0, po:0, used:false }), PG.get(p));
const stamCap = p => 60 + (clamp(p.stamina, 60, 120) - 60) * 2 / 3;               // 60 stamina = 60 pitches, 120 = 100, in a straight line
// 0 fresh, 1 at his limit: he throws up to 20 mph slower and his circle grows up to 2x, both in a straight line
function fatigue(){ const p = curPitcher(); return clamp(pg(p).pc / stamCap(p), 0, 1); }
// the best reliever who has not pitched yet: the closer saves the 8th and 9th of a close game
function pickReliever(t){
  const left = t.pen.filter(p => !pg(p).used);
  if (!left.length) return null;
  const cp = t.pen[t.pen.length - 1], lead = t === M.home ? M.score.home - M.score.away : M.score.away - M.score.home;
  if (M.inning >= 8 && lead >= 0 && lead <= 3 && left.includes(cp)) return cp;
  const rest = left.filter(p => p !== cp);
  return (rest.length ? rest : left).slice().sort((a, b) => b.ovr - a.ovr)[0];
}
function changePitcher(t, nx){
  if (!nx || pg(nx).used) return false;
  if (t === M.home) M.pitcherHome = nx; else M.pitcherAway = nx;
  pg(nx).used = true; nx.st.ip = nx.st.ip || 0;
  if (!nx.pitches[pitchSel]) pitchSel = 'FB';
  say('NEW PITCHER: ' + nx.name.toUpperCase());
  return true;
}
// he is taken out once he has gone at least 3 innings and then reaches his limit, or has given up more runs than his pitches / 10
function pullCheck(){
  const t = fldTeam(), p = curPitcher(), g = pg(p);
  if (g.po < 9) return;
  if (g.pc >= stamCap(p) || g.r > g.pc / 10) changePitcher(t, pickReliever(t));
}""")
rep("  return base * (1 + fatigue() * .55);", "  return base * (1 + fatigue());")
rep("- fatigue() * 3);", "- fatigue() * 20);")
rep("  if (M.top) M.pcHome++; else M.pcAway++;", "  pg(curPitcher()).pc++; if (M.top) M.pcHome++; else M.pcAway++;")
# a quick sim at-bat is about four pitches
rep("  const b = M.batter, p = curPitcher();\n  // Ratings swing the result hard", "  const b = M.batter, p = curPitcher();\n  pg(p).pc += ri(3, 5);\n  // Ratings swing the result hard")
# what he gave up
rep("  if (runs) p.st.er += runs;\n  M.outs += out; p.st.po = (p.st.po || 0) + out;", "  if (runs){ p.st.er += runs; pg(p).r += runs; }\n  M.outs += out; p.st.po = (p.st.po || 0) + out; pg(p).po += out;")
# check at the start of every plate appearance (so also at the start of every inning)
rep("function setupAtBat(){\n  M.balls = 0; M.strikes = 0;", "function setupAtBat(){\n  M.balls = 0; M.strikes = 0;\n  pullCheck();")
# new game: nobody has pitched
rep("  M.pitcherHome.st.ip = M.pitcherHome.st.ip || 0;\n  M.sp = { home: M.pitcherHome, away: M.pitcherAway };\n",
    "  M.pitcherHome.st.ip = M.pitcherHome.st.ip || 0;\n  PG.clear(); pg(M.pitcherHome).used = true; pg(M.pitcherAway).used = true;\n")
# decisions: the winning team's pitcher with the most outs gets the win, the losing team's pitcher who gave up the most runs the loss
a = s.index("  if (M.sp && M.score.home !== M.score.away){")
b = s.index("  }", s.index("wp.w = (wp.w || 0) + 1;")) + 4
s = s[:a] + """  if (M.score.home !== M.score.away){                                      // the decisions
    const hw = M.score.home > M.score.away, team = t => t.rot.concat(t.pen).filter(p => pg(p).used);
    const wp = team(hw ? M.home : M.away).sort((x, y) => pg(y).po - pg(x).po)[0], lp = team(hw ? M.away : M.home).sort((x, y) => pg(y).r - pg(x).r || pg(y).po - pg(x).po)[0];
    if (wp) wp.st.w = (wp.st.w || 0) + 1;
    if (lp) lp.st.l = (lp.st.l || 0) + 1;
  }
""" + s[b:]
# saving the game in progress: who has pitched and how much
rep("      spH:M.sp ? pitchers(M.home).indexOf(M.sp.home) : -1, spA:M.sp ? pitchers(M.away).indexOf(M.sp.away) : -1, t:Date.now() }));",
    "      pgH:pitchers(M.home).map(p => pg(p)), pgA:pitchers(M.away).map(p => pg(p)), t:Date.now() }));")
rep("  if (d.spH >= 0 && d.spA >= 0) M.sp = { home: pitchers(M.home)[d.spH], away: pitchers(M.away)[d.spA] };      // the starters who get the win and loss, same ones as before he quit\n",
    "  if (d.pgH && d.pgA){ PG.clear(); pitchers(M.home).forEach((p, i) => PG.set(p, d.pgH[i])); pitchers(M.away).forEach((p, i) => PG.set(p, d.pgA[i])); }      // who has pitched, and how much, same as before he quit\n")

# ── the player can bring in a reliever whenever he likes ──
rep("  button(W / 2 - 40, 174, 80, 18, 'BACK', () => { phase = userPitches() ? 'pitching' : 'atbat'; });\n}",
"""  const mine = M.meHome ? M.home : M.away, open = !(P && P.thrown) && mine.pen.some(p => !pg(p).used);
  button(W / 2 - 80, 166, 160, 18, 'CHANGE PITCHER', () => { if (open) phase = 'pitchpick'; }, open ? '#6a3aa8' : '#1a2230');
  button(W / 2 - 40, 190, 80, 18, 'BACK', () => { phase = userPitches() ? 'pitching' : 'atbat'; });
}
// pick a reliever: only pitchers who have not been in yet
function drawPitchPick(){
  btns = [];
  R(0, 0, W, H, '#0b1018f0');
  const mine = M.meHome ? M.home : M.away, cur = M.meHome ? M.pitcherHome : M.pitcherAway;
  textb('BRING IN A PITCHER', W / 2, 8, '#ffd23f', 10, 'center');
  textb('a pitcher who has been taken out cannot come back', W / 2, 24, UI.ice, 6, 'center');
  const list = mine.rot.concat(mine.pen).filter(p => p !== cur);
  list.forEach((p, i) => {
    const y = 36 + i * 15, x = W / 2 - 150, used = pg(p).used || mine.rot.includes(p), on = !used;
    R(x, y, 300, 13, on ? '#1b3e78' : '#1a2030');
    textb(mine.rot.includes(p) ? 'SP' : p === mine.pen[mine.pen.length - 1] ? 'CP' : 'RP', x + 4, y + 3, on ? UI.yellow : '#667', 6);
    textb(p.name, x + 24, y + 3, on ? '#ffffff' : '#667', 7, 'left', 130);
    [['VEL', p.velocity], ['CTL', p.control], ['STA', p.stamina]].forEach(([l, v], j) => textb(l + ' ' + v, x + 162 + j * 44, y + 3, on ? '#cfe0ff' : '#667', 6));
    if (pg(p).used) textb('USED', x + 296, y + 3, '#ff8a7a', 6, 'right');
    else if (mine.rot.includes(p)) textb('STARTER', x + 296, y + 3, '#667', 6, 'right');
    if (on) btns.push({ x, y, w:300, h:13, fn: () => { changePitcher(mine, p); phase = userPitches() ? 'pitching' : 'atbat'; nextPitch(); } });
  });
  button(W / 2 - 40, H - 22, 80, 16, 'BACK', () => phase = 'gmenu');
}""")
rep("  else if (phase === 'gmenu'){ drawBatterViewSafe(dt); drawGameMenu(); }", "  else if (phase === 'gmenu'){ drawBatterViewSafe(dt); drawGameMenu(); }\n  else if (phase === 'pitchpick'){ drawBatterViewSafe(dt); drawPitchPick(); }")
s = s.replace("BUILD = '11-04w'", "BUILD = '11-04x'")
rep("runToggle, runBack, drawPlay, get P(){ return P; },", "runToggle, runBack, drawPlay, PG, pg, stamCap, pullCheck, changePitcher, fatigue, fastballMph, spread, get P(){ return P; },")
open('index.html', 'w', encoding='utf-8').write(s)
import re
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
