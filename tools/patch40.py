s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

# ── a game in progress is saved (the season already was): on every pitch and whenever the app is closed or hidden ──
rep("function gameOver(){\n  M.over = true; phase = 'over';", '''// ── saving a game in progress. The season (G) saves as before; this writes down where the game stands so it can be picked up again. ──
const MSAVE = 'retrobaseball.match.v1';
function snapMatch(){
  try {
    if (!M || M.over || !G || phase === 'menu' || phase === 'over') return;
    const bt = batTeam(), pitchers = t => t.rot.concat(t.pen);
    localStorage.setItem(MSAVE, JSON.stringify({ v:1, day:G.day, opp:G.teams.indexOf(M.meHome ? M.away : M.home), meHome:M.meHome, mode:M.mode,
      inning:M.inning, top:M.top, outs:M.outs, balls:M.balls, strikes:M.strikes, score:M.score, ls:M.ls, H:M.H, E:M.E, pcHome:M.pcHome, pcAway:M.pcAway,
      lineHome:M.lineHome, lineAway:M.lineAway, bases:M.bases.map(p => p ? bt.lineup.indexOf(p) : null), bi:{ home:M.home._bi || 0, away:M.away._bi || 0 },
      pH:pitchers(M.home).indexOf(M.pitcherHome), pA:pitchers(M.away).indexOf(M.pitcherAway), t:Date.now() }));
  } catch (e){}
}
const matchSnap = () => { try { const d = JSON.parse(localStorage.getItem(MSAVE)); return d && d.v === 1 && G && d.day === G.day && G.day < G.seasonLen ? d : null; } catch (e){ return null; } };
function clearMatchSnap(){ try { localStorage.removeItem(MSAVE); } catch (e){} }
function resumeMatch(){
  const d = matchSnap(); if (!d) return false;
  startGame(d.opp, d.meHome, { mode:d.mode });
  const pitchers = t => t.rot.concat(t.pen);
  Object.assign(M, { inning:d.inning, top:d.top, outs:d.outs, score:d.score, ls:d.ls, H:d.H, E:d.E, pcHome:d.pcHome, pcAway:d.pcAway, lineHome:d.lineHome, lineAway:d.lineAway });
  M.home._bi = d.bi.home; M.away._bi = d.bi.away;
  if (d.pH >= 0) M.pitcherHome = pitchers(M.home)[d.pH]; if (d.pA >= 0) M.pitcherAway = pitchers(M.away)[d.pA];
  const bt = batTeam(); M.bases = d.bases.map(i => i == null || i < 0 ? null : bt.lineup[i]);
  setupAtBat(); M.balls = d.balls; M.strikes = d.strikes;
  return true;
}
function gameOver(){
  clearMatchSnap();
  M.over = true; phase = 'over';''')
# saves: every pitch, and whenever the app is closed, backgrounded or reloaded
rep("function afterPitch(){\n  const o = P.outcome;", "function afterPitch(){\n  snapMatch();\n  const o = P.outcome;")
rep("function endPA(res){\n  applyPlay(res);                                           // updates the count-free stuff: outs, runners, runs\n}",
    "function endPA(res){\n  applyPlay(res);                                           // updates the count-free stuff: outs, runners, runs\n  snapMatch();\n}\nfunction saveEverything(){ try { if (G) save(); snapMatch(); } catch (e){} }\naddEventListener('pagehide', saveEverything);\naddEventListener('beforeunload', saveEverything);\ndocument.addEventListener('visibilitychange', () => { if (document.hidden) saveEverything(); });")
# a new team wipes the old game
rep("function newGame(teamAb){", "function newGame(teamAb){\n  try { localStorage.removeItem('retrobaseball.match.v1'); } catch (e){}")
# the title screen
rep("""      button(W / 2 - 70, 116, 140, 22, G.day < G.seasonLen ? `PLAY GAME ${G.day + 1}/${G.seasonLen}` : 'SEASON DONE', () => {
        if (G.day >= G.seasonLen) return;
        const s = G.sched[G.day]; startGame(s.opp, s.home);
      }, '#2f6fe0');""", """      const snap = matchSnap();
      if (snap){
        const nm = `${snap.top ? 'TOP' : 'BOT'} ${snap.inning}  ${snap.score.away}-${snap.score.home}`;
        button(W / 2 - 108, 116, 150, 22, `RESUME ${nm}`, () => { if (!resumeMatch()) clearMatchSnap(); }, '#2f6fe0');
        button(W / 2 + 48, 116, 60, 22, 'RESTART', () => { clearMatchSnap(); if (G.day < G.seasonLen){ const s = G.sched[G.day]; startGame(s.opp, s.home); } }, '#2a1a1a', '#fff', 7);
      } else button(W / 2 - 70, 116, 140, 22, G.day < G.seasonLen ? `PLAY GAME ${G.day + 1}/${G.seasonLen}` : 'SEASON DONE', () => {
        if (G.day >= G.seasonLen) return;
        const s = G.sched[G.day]; startGame(s.opp, s.home);
      }, '#2f6fe0');""")
rep("runToggle, runBack, drawPlay,", "runToggle, runBack, drawPlay, snapMatch, resumeMatch, matchSnap, startGame2: startGame,")
s = s.replace("BUILD = '11-04n'", "BUILD = '11-04o'")
open('index.html', 'w', encoding='utf-8').write(s)
import re
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
