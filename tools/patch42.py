s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── 1) what gets counted ──
rep("const newStat = () => ({ ab:0, h:0, hr:0, rbi:0, r:0, bb:0, k:0, ip:0, er:0, ko:0, w:0, l:0, sb:0, pa:0 });",
    "const newStat = () => ({ ab:0, h:0, d:0, t:0, hr:0, rbi:0, r:0, bb:0, hbp:0, sf:0, k:0, ip:0, po:0, er:0, ko:0, ha:0, bba:0, fbn:0, fbs:0, w:0, l:0, sb:0, pa:0 });")
rep("    if (res !== 'error'){ st.h++; if (res === 'hr') st.hr++; st.rbi += runs; }",
    "    if (res !== 'error'){ st.h++; if (res === 'hr') st.hr++; if (res === 'double') st.d = (st.d || 0) + 1; if (res === 'triple') st.t = (st.t || 0) + 1; p.st.ha = (p.st.ha || 0) + 1; st.rbi += runs; }")
rep("    case 'hr': { st.ab++; st.h++; st.hr++;", "    case 'hr': { st.ab++; st.h++; st.hr++; p.st.ha = (p.st.ha || 0) + 1;")
rep("    case 'triple': st.ab++; st.h++;", "    case 'triple': st.ab++; st.h++; st.t = (st.t || 0) + 1; p.st.ha = (p.st.ha || 0) + 1;")
rep("    case 'double': { st.ab++; st.h++;", "    case 'double': { st.ab++; st.h++; st.d = (st.d || 0) + 1; p.st.ha = (p.st.ha || 0) + 1;")
rep("    case 'single': { st.ab++; st.h++;", "    case 'single': { st.ab++; st.h++; p.st.ha = (p.st.ha || 0) + 1;")
rep("runs += advance(1, false); st.rbi += runs; txt = 'SAC FLY'; }",
    "runs += advance(1, false); st.rbi += runs; st.ab--; st.sf = (st.sf || 0) + 1; txt = 'SAC FLY'; }      // a sacrifice fly is not an at-bat")
rep("    case 'bb':  st.bb++;", "    case 'bb':  st.bb++; p.st.bba = (p.st.bba || 0) + 1;")
rep("    case 'hbp': runs = walkAdvance();", "    case 'hbp': st.hbp = (st.hbp || 0) + 1; runs = walkAdvance();")
rep("  M.outs += out;\n  say(txt);", "  M.outs += out; p.st.po = (p.st.po || 0) + out;                       // the outs he got: his innings pitched\n  say(txt);")
rep("  P.mph = Math.round((type === 'FB' ? fb : fb - (CFG.OFFSPEED_SLOW[type] || 12)) - fatigue() * 3);",
    "  P.mph = Math.round((type === 'FB' ? fb : fb - (CFG.OFFSPEED_SLOW[type] || 12)) - fatigue() * 3);\n  if (type === 'FB'){ const ps = curPitcher().st; ps.fbn = (ps.fbn || 0) + 1; ps.fbs = (ps.fbs || 0) + P.mph; }      // for his average fastball")
# the starters get the win and the loss
rep("  M.pitcherHome.st.ip = M.pitcherHome.st.ip || 0;\n", "  M.pitcherHome.st.ip = M.pitcherHome.st.ip || 0;\n  M.sp = { home: M.pitcherHome, away: M.pitcherAway };\n")
rep("function gameOver(){\n  clearMatchSnap();\n  M.over = true; phase = 'over';",
"""function gameOver(){
  clearMatchSnap();
  M.over = true; phase = 'over';
  if (M.sp && M.score.home !== M.score.away){                              // the starters get the decision
    const hw = M.score.home > M.score.away, wp = (hw ? M.sp.home : M.sp.away).st, lp = (hw ? M.sp.away : M.sp.home).st;
    wp.w = (wp.w || 0) + 1; lp.l = (lp.l || 0) + 1;
  }""")

# ── 2) the title menu: LEAGUE LEADERS takes the place of NEW TEAM ──
rep("      button(W / 2 + 40, 164, 68, 18, 'NEW TEAM', () => menu = 'pick', '#2a1a1a');",
    "      button(W / 2 + 40, 164, 68, 18, 'LEADERS', () => { menu = 'stats'; statsScroll = 0; }, '#2f6fe0', '#fff', 7);")
rep("  else if (menu === 'stand'){", "  else if (menu === 'stats'){ drawStats(); return; }\n  else if (menu === 'stand'){")

# ── 3) the leaders page ──
rep("function drawOver(){", r'''// ── league leaders: batters or pitchers, every player or each team's average; tap a column to rank by it (tap again to flip) ──
let statsView = 'bat', statsTeam = -1, statsScroll = 0, statsBy = 'player';
const statsSort = { bat:{ k:'avg', asc:false }, pit:{ k:'era', asc:true } };
const n3 = v => v >= 1 ? v.toFixed(3) : v.toFixed(3).replace('0.', '.');
const poOf = st => st.po > 0 ? st.po : (st.ip || 0) * 3;
const ipText = st => { const o = poOf(st); return Math.floor(o / 3) + '.' + (o % 3); };
// cnt: a counting stat (a team row shows the average per player); the rest are rates, worked out from the team's totals
const STAT_COLS = {
  bat: [
    { k:'avg', h:'AVG', v:t => t.ab ? t.h / t.ab : null, f:n3 },
    { k:'obp', h:'OBP', v:t => { const d = t.ab + t.bb + (t.hbp || 0) + (t.sf || 0); return d ? (t.h + t.bb + (t.hbp || 0)) / d : null; }, f:n3 },
    { k:'r', h:'R', cnt:1, v:t => t.r || 0, f:v => v },
    { k:'hr', h:'HR', cnt:1, v:t => t.hr || 0, f:v => v },
    { k:'slg', h:'SLG', v:t => t.ab ? (t.h + (t.d || 0) + 2 * (t.t || 0) + 3 * (t.hr || 0)) / t.ab : null, f:n3 },
    { k:'rbi', h:'RBI', cnt:1, v:t => t.rbi || 0, f:v => v },
  ],
  pit: [
    { k:'era', h:'ERA', v:t => poOf(t) ? (t.er || 0) * 27 / poOf(t) : null, f:v => v.toFixed(2) },
    { k:'ko', h:'K', cnt:1, v:t => t.ko || 0, f:v => v },
    { k:'fb', h:'FB', v:t => t.fbn ? t.fbs / t.fbn : null, f:v => v.toFixed(1) },
    { k:'whip', h:'WHIP', v:t => poOf(t) ? ((t.ha || 0) + (t.bba || 0)) * 3 / poOf(t) : null, f:v => v.toFixed(2) },
    { k:'ip', h:'IP', cnt:1, v:t => poOf(t), f:(v, t) => ipText(t), fa:v => (v / 3).toFixed(1) },
    { k:'w', h:'W', cnt:1, v:t => t.w || 0, f:v => v },
    { k:'l', h:'L', cnt:1, v:t => t.l || 0, f:v => v },
  ],
};
function statRows(){
  const rows = [], bat = statsView === 'bat';
  G.teams.forEach((t, ti) => {
    if (statsBy === 'player' && statsTeam >= 0 && ti !== statsTeam) return;
    const mine = ti === G.team;
    const list = bat ? (mine ? G.cards.filter(c => !isPitcher(c)) : t.lineup) : (mine ? G.cards.filter(isPitcher) : t.rot.concat(t.pen));
    const used = list.filter(p => { const st = p.st || {}; return bat ? (st.pa || 0) > 0 : (poOf(st) > 0 || (st.fbn || 0) > 0); });
    if (statsBy === 'player') used.forEach(p => rows.push({ p, t, ti, st:p.st }));
    else if (used.length){
      const agg = {}; Object.keys(newStat()).forEach(k => agg[k] = 0);
      used.forEach(p => { Object.keys(agg).forEach(k => agg[k] += (p.st[k] || 0)); agg.po += poOf(p.st) - (p.st.po || 0); });
      rows.push({ p:{ name:t.city + ' ' + t.nick }, t, ti, st:agg, n:used.length });
    }
  });
  const cols = STAT_COLS[statsView], so = statsSort[statsView], col = cols.find(c => c.k === so.k) || cols[0];
  rows.forEach(r => { let v = col.v(r.st); if (v !== null && r.n && col.cnt) v /= r.n; r.v = v; });
  rows.sort((a, b) => (a.v === null) - (b.v === null) || (so.asc ? a.v - b.v : b.v - a.v));
  return { rows, cols, col };
}
function drawStats(){
  btns = [];
  uiBg();
  R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff');
  ptitle('LEAGUE LEADERS', 10, 3, 9, '#ffffff', 'left');
  const pill = (x, w, l, on, fn) => {
    if (on) R(x, 22, w, 14, UI.yellow); else uiBox(x, 22, w, 14);
    textb(l, x + w / 2, 25, on ? '#241a00' : '#ffffff', 6, 'center');
    btns.push({ x, y:22, w, h:14, fn });
  };
  pill(8, 56, 'BATTERS', statsView === 'bat', () => { statsView = 'bat'; statsScroll = 0; });
  pill(68, 56, 'PITCHERS', statsView === 'pit', () => { statsView = 'pit'; statsScroll = 0; });
  pill(128, 54, statsBy === 'team' ? 'BY TEAM' : 'PLAYERS', false, () => { statsBy = statsBy === 'team' ? 'player' : 'team'; statsScroll = 0; });
  if (statsBy === 'player'){
    const tn = statsTeam < 0 ? 'ALL TEAMS' : G.teams[statsTeam].ab + ' ' + G.teams[statsTeam].nick;
    button(W - 116, 22, 14, 14, '<', () => { statsTeam = statsTeam <= -1 ? G.teams.length - 1 : statsTeam - 1; statsScroll = 0; }, '#1a2030', '#fff', 8);
    uiBox(W - 100, 22, 84, 14); textb(tn, W - 58, 25, '#ffffff', 6, 'center', 80);
    button(W - 14 - 2, 22, 14, 14, '>', () => { statsTeam = statsTeam >= G.teams.length - 1 ? -1 : statsTeam + 1; statsScroll = 0; }, '#1a2030', '#fff', 8);
  }
  const { rows, cols, col } = statRows(), so = statsSort[statsView];
  const nameW = Math.max(70, Math.round(W * .27)), x0 = 8, cx0 = x0 + 12 + nameW + 22, cw = Math.floor((W - 30 - cx0) / cols.length);
  const hy = 41; R(0, hy - 2, W, 11, UI.blueDD);
  textb('#', x0, hy, UI.ice, 6); textb(statsBy === 'team' ? 'TEAM (PER-PLAYER AVG FOR COUNTS)' : statsView === 'bat' ? 'PLAYER' : 'PITCHER', x0 + 12, hy, UI.ice, 5, 'left', nameW + 20);
  if (statsBy === 'player') textb('TM', x0 + 12 + nameW, hy, UI.ice, 6);
  cols.forEach((c, i) => {
    const x = cx0 + i * cw, on = c.k === col.k;
    textb(c.h + (on ? (so.asc ? '^' : 'v') : ''), x + cw - 2, hy, on ? UI.yellow : UI.ice, 6, 'right');
    btns.push({ x:x - 2, y:hy - 3, w:cw, h:13, fn: () => { if (statsSort[statsView].k === c.k) statsSort[statsView].asc = !statsSort[statsView].asc; else statsSort[statsView] = { k:c.k, asc:c.k === 'era' || c.k === 'whip' || c.k === 'l' }; statsScroll = 0; } });
  });
  const rh = 11, top = 54, vis = Math.floor((H - top - 24) / rh), maxScroll = Math.max(0, rows.length - vis);
  statsScroll = clamp(statsScroll, 0, maxScroll);
  if (!rows.length) textb('No stats yet: play a game and they show up here.', W / 2, 100, '#ffffff', 7, 'center', W - 20);
  rows.slice(statsScroll, statsScroll + vis).forEach((r, i) => {
    const y = top + i * rh, mine = r.ti === G.team, tc = mine ? UI.yellow : '#ffffff';
    if (mine) R(0, y - 2, W, rh, 'rgba(255,210,63,.18)'); else if (i % 2) R(0, y - 2, W, rh, 'rgba(255,255,255,.06)');
    textb(String(statsScroll + i + 1), x0, y, UI.ice, 6);
    textb(r.p.name, x0 + 12, y, tc, 6, 'left', (statsBy === 'team' ? nameW + 20 : nameW) - 4);
    if (statsBy === 'player') textb(r.t.ab, x0 + 12 + nameW, y, mine ? UI.yellow : UI.ice, 6);
    cols.forEach((c, j) => {
      let v = c.v(r.st);
      const txt = v === null ? '-' : r.n && c.cnt ? (c.fa ? c.fa(v / r.n) : (v / r.n).toFixed(1)) : c.f(v, r.st);
      textb(txt, cx0 + j * cw + cw - 2, y, c === col ? (mine ? '#fff29a' : UI.yellow) : tc, 6, 'right');
    });
  });
  if (maxScroll > 0){
    button(W - 26, top - 2, 20, 18, '^', () => statsScroll = Math.max(0, statsScroll - 5), '#1a2030', '#fff', 8);
    button(W - 26, H - 44, 20, 18, 'v', () => statsScroll = Math.min(maxScroll, statsScroll + 5), '#1a2030', '#fff', 8);
  }
  textb('tap a column to rank by it', W / 2, H - 12, UI.ice, 6, 'center');
  button(8, H - 22, 50, 16, 'BACK', () => menu = 'title');
}
function drawOver(){''')
s = s.replace("BUILD = '11-04q'", "BUILD = '11-04r'")
rep("runToggle, runBack, drawPlay,", "runToggle, runBack, drawPlay, statRows, STAT_COLS, get statsBy(){ return statsBy; }, set statsBy(v){ statsBy = v; }, get statsView(){ return statsView; }, set statsView(v){ statsView = v; },")
open('index.html', 'w', encoding='utf-8').write(s)
import re
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
