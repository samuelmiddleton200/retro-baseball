s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80]); s = s.replace(a, b)

# a home run under 450 ft keeps the plain WHITE arc (it was drawn orange)
rep("g.strokeStyle = S.hr ? (S.hrOut ? 'rgba(80,170,255,.4)' : 'rgba(255,120,30,.35)') : 'rgba(255,255,255,.55)'; g.lineWidth = S.hr ? 1.2 : .9; g.beginPath();",
    "g.strokeStyle = 'rgba(255,255,255,.55)'; g.lineWidth = .9; g.beginPath();")

# ── the pause menu: two rows of three, and BACK along the bottom ──
a = s.index("function drawGameMenu(){"); b = s.index("// pick a reliever: only pitchers who have not been in yet")
s = s[:a] + """// SIM INNING: play out the rest of this inning without playing it. Everything: to the top of the next inning. One side only: the half you don't play is
// simmed anyway, so it runs until the next half that is yours (batting only, in the bottom: the rest of the bottom and the top that follows)
function simInning(){
  if (M.over) return;
  const mode = M.mode, inn0 = M.inning, side0 = M.top; let guard = 0;
  const half = () => { const side = M.top, inn = M.inning; while (!M.over && M.top === side && M.inning === inn && guard++ < 900) simPitch(); };
  half();                                                                                  // the rest of this half
  if (mode === 'full'){ while (!M.over && M.inning === inn0 && guard++ < 900) half(); }    // top of the next inning
  else { const mine = () => mode === 'offense' ? weBat() : !weBat(); while (!M.over && !mine() && guard++ < 900) half(); }
  if (M.over){ phase = 'over'; return; }
  nextPitch();
}
function drawGameMenu(){
  if (M.derby) return drawDerbyPause();
  btns = [];
  R(0, 0, W, H, '#0b1018e8');
  textb('WHAT DO YOU WANT TO PLAY?', W / 2, 30, '#ffd23f', 10, 'center');
  const bw = 106, bh = 27, gp = 6, x0 = W / 2 - (3 * bw + 2 * gp) / 2, xs = i => x0 + i * (bw + gp), y1 = 54, y2 = y1 + bh + gp + 2, y3 = y2 + bh + gp + 2, fs = 7;
  const modes = [['PLAY EVERYTHING', 'full'], ['BATTING ONLY', 'offense'], ['PITCHING ONLY', 'defense']];
  modes.forEach(([l, m], i) => button(xs(i), y1, bw, bh, l, () => {
    M.mode = m; phase = 'atbat';
    if ((m === 'offense' && !weBat()) || (m === 'defense' && weBat())){ simHalfIfNeeded(); if (!M.over && phase === 'atbat' && !P) nextPitch(); }   // the half you just skipped plays out now
    else nextPitch();
  }, M.mode === m ? '#2f6fe0' : '#1a2230', M.mode === m ? '#fff' : '#fff', fs));                       // the mode you are in is lit
  const mine = M.meHome ? M.home : M.away, open = !(P && P.thrown) && mine.pen.some(p => !pg(p).used);
  button(xs(0), y2, bw, bh, 'SIM INNING', () => simInning(), '#1a2230', '#fff', fs);
  button(xs(1), y2, bw, bh, 'SIM FULL GAME', () => simRest(), '#1a2230', '#fff', fs);
  button(xs(2), y2, bw, bh, 'CHANGE PITCHER', () => { if (open) phase = 'pitchpick'; }, open ? '#1a2230' : '#161b26', '#fff', fs);
  button(xs(0), y3, 3 * bw + 2 * gp, bh, 'SAVE AND EXIT', () => { saveEverything(); M = null; P = null; BALL = null; phase = 'menu'; menu = 'title'; }, '#1a2230', '#fff', 8);      // the game is written down where it stands; RESUME on the main menu picks it up
}
""" + s[b:]
s = s.replace("BUILD = '11-11s'", "BUILD = '11-11t'").replace("gl3d.js?v=11-11s", "gl3d.js?v=11-11t")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
