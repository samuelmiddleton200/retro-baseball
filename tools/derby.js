// ───────────────────────────────────────────────────────────────────────────
//  HOME RUN DERBY (MINIGAMES)
//  10 outs. A pitcher alone on the field throws 70 mph straight down the middle. A ball in play scores its feet; a home run adds 250;
//  a home run of 470 ft or more adds 250 more. A ball that is not a home run is an out. Fouls count for nothing. Coins come at the end only.
// ───────────────────────────────────────────────────────────────────────────
const DERBY_OUTS = 10, DERBY_MPH = 70, DERBY_FAR = 470;
const DPITCH = new Image(); DPITCH.src = 'assets/fields/derby_pitch.png?b=11-09a';        // the stadium from the batter's end
const DHIT = new Image(); DHIT.src = 'assets/fields/derby_hit.png?b=11-09a';              // the same stadium from high above
const derbyReady = () => ready(DPITCH) && ready(DHIT);
// feet on the field -> a pixel in the hit-view picture (1873 x 840). Fitted to the painted field: home plate, the mound, first base, the fence in centre and at the poles.
const DH = { y0:170, K:62230, c:98, xc:935, kx:1244, hs:.85, IW:1873, IH:840 };
function derbyPt(d, lat, h){
  const dd = Math.max(d, -40) + DH.c, s = DH.kx / dd, sc = H / DH.IH, x0 = W / 2 - DH.IW * sc / 2;
  return { x: x0 + (DH.xc + lat * s) * sc, y: (DH.y0 + DH.K / dd - h * s * DH.hs) * sc, s: s * sc };
}
let derbyPick = null, derbyScroll = 0;

function derbyStart(card){
  if (!G || !card || !derbyReady()) return false;
  const me = myTeam(), opp = G.teams[(G.team + 1) % G.teams.length];
  M = {
    home: opp, away: me, meHome: false,
    inning:1, top:true, outs:0, bases:[null,null,null], score:{ home:0, away:0 },
    balls:0, strikes:0, lineHome:0, lineAway:0, ls:{ away:[], home:[] }, H:{ away:0, home:0 }, E:{ away:0, home:0 },
    pitcherHome: opp.rot[0], pitcherAway: me.rot[0], pcHome:0, pcAway:0, line:[], mode:'full',
    park: { wall:'#1c3b40', wallH:26, feature:'none', pad:0, lf:330, cf:400, rf:330, night:false, excite:0 }, msg:null, msgT:0, over:false, exc:0,
  };
  M.uni = pickUniforms(M.home, M.away);
  M.coins0 = G.coins; M.earn = {}; M.rep = {}; M.pitchSimmed = false;
  M.batter = card; M.catcher = opp.lineup[0];
  M.derby = { card, outs:0, score:0, hr:0, dist:0, balls:0, longest:0, pop:null, fin:null, hrParty:[] };
  PG.clear(); pg(M.pitcherHome).used = true; pg(M.pitcherAway).used = true;
  if (!G.derby) G.derby = { best:0, plays:0, longest:0 };
  swing = null; BALL = null; P = null; aerTrail = []; DTRAIL = [];
  phase = 'atbat'; nextPitch();
  return true;
}
// every pitch: 70 mph, dead centre, no break
const derbyMoundShift = () => { const st = curStadium(); return { x:st.shift[0] * TU, y:st.shift[1] * H }; };
function derbyThrow(){
  P.type = 'FB'; P.tx = 0; P.ty = 0; P.br = [0, 0]; P.mph = DERBY_MPH; P.quality = 100;
  P.dur = CFG.MOUND_FT / (DERBY_MPH * CFG.MPH_TO_FPS) * 1000 / CFG.PITCH_TIME_SCALE;
  P.thrown = true; P.t = 0; P.state = 'flight';
}
// how far it went: the farthest point of its flight before it first touched the ground (a ball that hit the wall counts to the wall)
function derbyDist(B){
  let m = 0; const end = Math.min(B.path.length - 1, Math.ceil(B.T * 120) + 1);
  for (let k = 0; k <= end; k++){ const r = Math.hypot(B.path[k][0], B.path[k][1]); if (r > m) m = r; }
  return Math.max(m, B.carry || 0);
}
// the ball is in play: no fielders. It is judged where it comes down (a home run when it reaches the seats), then the next pitch.
function derbyStepPlay(dt){
  const B = BALL, D = M.derby;
  P.playT += dt; if (swing) swing.t += dt;
  stepBall(dt * CFG.TIME_SCALE);
  if (B.hr && B.hrG == null) B.hrG = hrGoneTime(B);
  if (!B.judged){
    if (B.foul){ if (B.t >= B.tJudge){ B.judged = true; B.play = 'foul'; say('FOUL BALL'); P.dres = 'foul'; } }
    else if (B.hr ? B.t >= B.hrG : B.t >= B.T){
      B.judged = true; B.play = 'derby'; P.dres = 'play';
      const d = Math.round(derbyDist(B)), far = B.hr && d >= DERBY_FAR, pts = d + (B.hr ? 250 : 0) + (far ? 250 : 0);
      D.score += pts; D.dist += d; D.balls++; D.longest = Math.max(D.longest, d);
      if (B.hr){ D.hr++; M.exc = 1.4; } else { D.outs++; M.outs = D.outs; }
      M.strikes = 0;                                                    // the next ball is a fresh at-bat
      D.pop = { t:0, d, pts, hr:B.hr, far, kind: B.hr ? (far ? 'OUT OF THE PARK!' : 'HOME RUN!') : B.grounder ? 'GROUND OUT' : B.la > 38 ? 'POP OUT' : B.la > 18 ? 'FLY OUT' : 'LINE OUT' };
      say(D.pop.kind);
    }
  }
  const tEnd = B.foul ? B.tJudge + .5 : B.hr ? (B.hrG || B.T) + (B.carry >= 450 ? 2.9 : 2.3) : Math.max(B.T, .8) + 1.3;
  if ((B.judged && B.t >= tEnd) || P.playT > 14000){ P.state = 'result'; P.hold = 9999; P.outcome = B.foul ? 'foul' : 'derby'; }
}
function derbyAfter(){
  const D = M.derby, o = P.outcome;
  if (o === 'called' || o === 'swingmiss'){
    M.strikes++; D.k = (D.k || 0) + 1;
    if (M.strikes >= 3){ D.outs++; M.outs = D.outs; M.strikes = 0; say('STRIKE THREE'); }
  }
  D.pop = null; DTRAIL = [];
  if (D.outs >= DERBY_OUTS) return derbyEnd();
  nextPitch();
}
function derbyEnd(){
  const D = M.derby, hrCoins = D.hr * 100, distCoins = Math.round(D.dist / 5);
  G.coins += hrCoins + distCoins;
  const gd = G.derby || (G.derby = { best:0, plays:0, longest:0 }), nb = D.score > gd.best;
  if (nb) gd.best = D.score; gd.plays++; gd.longest = Math.max(gd.longest || 0, D.longest);
  D.fin = { hrCoins, distCoins, nb };
  M.over = true; phase = 'over'; save();
}

// ── drawing ────────────────────────────────────────────────────────────────
let DTRAIL = [];
function derbyHUD(){
  const D = M.derby, x = 10, y = 15, w = 128 * TU * 1.2 * 1.3, h = 74 * TU * 1.2;
  hudPanel(x, y, w, h, '#00153c');
  tt('HOME RUN DERBY', x + w / 2, y + 11 * TU * 1.2, 17, '#ffd23f', 'center', 118);
  tt('SCORE', x + 8, y + 33 * TU * 1.2, 15, '#9fb4dc', 'left');
  tt(D.score.toLocaleString(), x + w - 8, y + 33 * TU * 1.2, 24, '#ffffff', 'right');
  tt('HR ' + D.hr, x + 8, y + 56 * TU * 1.2, 17, '#ffffff', 'left');
  for (let i = 0; i < DERBY_OUTS; i++){                                // ten dots: one goes dark with every out
    const cx = x + w - 8 - (DERBY_OUTS - 1 - i) * 8 * TU * 1.2 * 1.05 - 3, cy = y + 56 * TU * 1.2;
    g.fillStyle = i < D.outs ? '#e24b3b' : '#31456f'; g.beginPath(); g.arc(cx, cy, 2.4 * TU * 1.2, 0, 7); g.fill();
  }
  if (G.derby && G.derby.best) tt('BEST ' + G.derby.best.toLocaleString(), x + w / 2, y + h + 8 * TU, 14, '#cfe0ff', 'center');
}
// the pitcher, the batter and the catcher stand where they do in the game's own high view (the same painted sprites, still)
function derbyPeople(){
  if (!(GPF.ready && GP.ready)) return;
  const ft = fldTeam(), bt = batTeam(), b = M.batter, lefty = b.bats === 'L';
  [{ k:'cat', d:-3.4, lat:0, bat:1, man:ft.lineup[7] || ft.lineup[0], team:ft },
   { k:'bat', d:.7, lat: lefty ? 3 : -3, man:b, team:bt },
   { k:'pit', d:60.5, lat:0, man:curPitcher(), team:ft }].forEach(o => {
    const p = gxPerson(o.k, o.k, o.man, o.team, o.lat, -o.d, 0, null), q = derbyPt(o.d, o.lat, 0), hPx = clamp(Math.round(6.2 * q.s * DH.hs * 1.05 * .85), 10, 13);
    GPSK = p.skin || '';
    gpStamp(GPF.img[0], 'FD0', p.cap, q.x, q.y, hPx / TU, false, .96);
  });
}
function drawDerbyHit(B){
  const D = M.derby, sc = H / DH.IH, x0 = W / 2 - DH.IW * sc / 2;
  g.fillStyle = '#05070b'; g.fillRect(0, 0, W, H); g.imageSmoothingEnabled = false;
  if (ready(DHIT)) g.drawImage(DHIT, x0, 0, DH.IW * sc, H);
  derbyPeople();
  if (B.t < .05) DTRAIL = [];
  const gone = B.hr && B.hrG != null && B.t >= B.hrG, air = B.t < B.T && !gone;
  if (air){ DTRAIL.push([B.lat, B.h + .4 + BALL_LIFT, -B.d]); if (DTRAIL.length > 290) DTRAIL.shift(); }
  const Pp = (x, y, z) => derbyPt(-z, x, y);
  if (DTRAIL.length > 1 && !B.hr){
    g.strokeStyle = 'rgba(255,255,255,.6)'; g.lineWidth = .9; g.beginPath();
    DTRAIL.forEach((t, i) => { const q = Pp(...t); i ? g.lineTo(q.x, q.y) : g.moveTo(q.x, q.y); }); g.stroke();
  }
  if (gone && !B.endPt && DTRAIL.length) B.endPt = DTRAIL[DTRAIL.length - 1];
  if (gone){ DTRAIL.splice(0, 5); }                                       // in the seats: the tail catches up and the fire burns out
  if (B.hr && DTRAIL.length > 3){
    const fade = gone ? clamp(1 - (B.t - B.hrG) / .75, 0, 1) : 1;
    if (fade > 0) hrFire({ trail: DTRAIL, hrFar: (B.carry || 0) >= 450, fade }, Pp);
  }
  // the ball and the spot it comes down
  if (!gone && !B.foul || (B.foul && B.t < B.tJudge)){
    const gq = derbyPt(B.d, B.lat, 0), q = derbyPt(B.d, B.lat, B.h + BALL_LIFT);
    R(Math.round(gq.x - 2), Math.round(gq.y), 4, 1, 'rgba(20,14,6,.4)');
    if (q.y < 4){ g.fillStyle = '#fff'; g.beginPath(); g.moveTo(q.x, 2); g.lineTo(q.x - 3, 7); g.lineTo(q.x + 3, 7); g.fill(); }
    else if (!ballPx(q.x, q.y, 3)) drawBall(q.x, q.y, 1.6);                // the same little pixel baseball as the normal hit view
  }
  if (B.judged && !B.hr && !B.foul){
    const pk = B.path[Math.min(B.path.length - 1, Math.floor(B.T * 120))], lp = derbyPt(pk[1], pk[0], 0), age = Math.min(1, (B.t - B.T) / .6);
    g.strokeStyle = `rgba(255,255,255,${.9 * (1 - age)})`; g.lineWidth = 1.2; g.beginPath(); g.ellipse(lp.x, lp.y, 3 + age * 10, 1.4 + age * 4, 0, 0, 7); g.stroke();
  }
  // a burst where a home run reaches the seats
  if (B.hr && B.hrG != null && B.t >= B.hrG){
    const a = B.t - B.hrG, e = D.pop, far = e && e.far, k = Math.min(1, a / 1.2);
    const pe = B.endPt || (DTRAIL.length ? DTRAIL[DTRAIL.length - 1] : null);
    if (pe && a < 1.3){
      const q = derbyPt(-pe[2], pe[0], pe[1]), cols = far ? ['#fff6c0', '#ffd23f', '#ff8a1c'] : ['#ffffff', '#9be9ff', '#ffd23f'];
      for (let i = 0; i < (far ? 26 : 16); i++){ const an = i * 2.4 + 1, rr = 4 + k * (far ? 34 : 22) * (.6 + (i % 5) * .12);
        R(q.x + Math.cos(an) * rr, q.y + Math.sin(an) * rr * .8 + k * k * 6, 2, 2, cols[i % 3]); }
    }
  }
  const cur = Math.round(Math.hypot(B.d, B.lat));
  if (!B.foul) tt(`${Math.round(B.ev)} MPH   ${B.judged && D.pop ? D.pop.d : cur} FT`, W / 2, ty(150), 20, '#ffffff', 'center');
  if (D.pop){
    const e = D.pop; e.t += 16;
    const col = e.far ? '#7fd6ff' : e.hr ? '#ffd23f' : '#ffffff', sz = e.hr ? 46 : 32, pul = e.hr ? 1 + .05 * Math.sin(e.t / 90) : 1;
    tt(e.kind, W / 2, ty(215), sz * pul, col, 'center');
    tt('+' + e.pts.toLocaleString(), W / 2, ty(285), 30, '#ffffff', 'center');
  } else if (B.foul) tt('FOUL BALL', W / 2, ty(215), 34, '#cfe0ff', 'center');
  derbyHUD();
}
function drawDerbyPause(){
  btns = [];
  R(0, 0, W, H, '#0b1018e8');
  const D = M.derby;
  textb('PAUSED', W / 2, 36, '#fff', 18, 'center');
  textb(`SCORE ${D.score.toLocaleString()}   HR ${D.hr}   OUTS ${D.outs}/${DERBY_OUTS}`, W / 2, 66, UI.ice, 8, 'center');
  button(W / 2 - 80, 100, 160, 22, 'RESUME', () => { phase = 'atbat'; }, '#2f6fe0');
  button(W / 2 - 80, 130, 160, 22, 'END DERBY (KEEP COINS)', () => { derbyEnd(); }, '#1a2230', '#fff', 7);
  button(W / 2 - 80, 160, 160, 18, 'QUIT (NO COINS)', () => { M = null; phase = 'menu'; menu = 'minigames'; }, '#2a1a1a', '#fff', 7);
}
function drawDerbyOver(){
  btns = [];
  R(0, 0, W, H, '#0b1018ee');
  const D = M.derby, F = D.fin;
  textb('DERBY OVER', W / 2, 8, '#ffd23f', 18, 'center');
  textb(`SCORE  ${D.score.toLocaleString()}`, W / 2, 33, '#fff', 12, 'center');
  textb(F.nb ? 'NEW BEST!' : `BEST  ${G.derby.best.toLocaleString()}`, W / 2, 49, F.nb ? '#54d67a' : UI.ice, 8, 'center');
  const rows = [[`${D.hr} HOME RUN${D.hr === 1 ? '' : 'S'}`, F.hrCoins], [`${D.dist.toLocaleString()} FT OF DISTANCE`, F.distCoins]];
  const y0 = 70, sp = 14, lx = W / 2 - 110, rx = W / 2 + 110;
  rows.forEach(([l, v], i) => { textb(l, lx, y0 + i * sp, UI.ice, 7, 'left'); textb('+' + v.toLocaleString(), rx, y0 + i * sp, '#ffffff', 7, 'right'); });
  const ty2 = y0 + rows.length * sp + 3; R(lx, ty2, 220, 1, '#2a5ba6');
  textb('TOTAL EARNED', lx, ty2 + 4, '#ffd23f', 8, 'left'); textb('+' + (F.hrCoins + F.distCoins).toLocaleString() + ' coins', rx, ty2 + 3, '#ffd23f', 9, 'right');
  button(W / 2 - 108, ty2 + 26, 100, 22, 'PLAY AGAIN', () => { const c = D.card; M = null; derbyStart(c); }, '#2f6fe0');
  button(W / 2 + 8, ty2 + 26, 100, 22, 'CONTINUE', () => { M = null; phase = 'menu'; menu = 'minigames'; }, '#1a2030', '#fff', 8);
}
// ── the menus: MINIGAMES, then pick a hitter ───────────────────────────────
function drawMinigames(){
  R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff'); ptitle('MINIGAMES', 10, 3, 10, '#ffffff', 'left'); coinText(G.coins, W - 8, 4, 8, UI.yellow, 'right');
  const bw = Math.min(300, W - 40), bx = W / 2 - bw / 2, by = 34;
  uiBox(bx, by, bw, 78);
  ptitle('HOME RUN DERBY', W / 2, by + 8, 12, UI.yellow);
  text('10 OUTS. 70 MPH DOWN THE MIDDLE. HIGH SCORE.', W / 2, by + 30, UI.ice, 6.5, 'center', bw - 12);
  const gd = G.derby || { best:0, plays:0 };
  text(gd.best ? `BEST ${gd.best.toLocaleString()}   LONGEST ${(gd.longest || 0)} FT` : 'NO SCORE YET', W / 2, by + 42, '#ffffff', 6.5, 'center', bw - 12);
  button(bx + bw / 2 - 50, by + 54, 100, 18, derbyReady() ? 'PLAY' : 'LOADING', () => { if (derbyReady()){ derbyPick = null; derbyScroll = 0; menu = 'derbypick'; } }, derbyReady() ? '#2f6fe0' : '#161b26', '#fff', 8);
  button(10, H - 22, 70, 18, 'BACK', () => menu = 'title');
}
function drawDerbyPick(){
  uiBg();
  R(0, 0, W, 17, UI.blueDD); R(0, 17, W, 2, '#ffffff'); ptitle('PICK YOUR HITTER', 10, 3, 10, '#ffffff', 'left');
  const list = G.cards.filter(c => !isPitcher(c)).sort((a, b) => ovrOf(b) - ovrOf(a));
  if (derbyPick && !list.includes(derbyPick)) derbyPick = null;
  const cw = 44, ch = 62, per = Math.floor((W - 16) / (cw + 4)), rows = Math.ceil(list.length / per), vis = H - 66, maxS = Math.max(0, rows * (ch + 6) - vis);
  derbyScroll = clamp(derbyScroll, 0, maxS);
  g.save(); g.beginPath(); g.rect(0, 21, W, vis); g.clip();
  list.forEach((c, i) => {
    const x = 8 + (i % per) * (cw + 4), y = 24 + Math.floor(i / per) * (ch + 6) - derbyScroll;
    if (y > 21 + vis || y + ch < 21) return;
    drawCard(x, y, c, cw, ch, frame, { });
    if (c === derbyPick){ g.strokeStyle = UI.yellow; g.lineWidth = 2; g.strokeRect(x - 1, y - 1, cw + 2, ch + 2); }
    btns.push({ x, y:Math.max(y, 21), w:cw, h:Math.min(y + ch, 21 + vis) - Math.max(y, 21), fn: () => { derbyPick = c; } });
  });
  g.restore();
  if (maxS > 0){ button(W - 26, 24, 20, 20, '▲', () => derbyScroll = Math.max(0, derbyScroll - 60)); button(W - 26, H - 70, 20, 20, '▼', () => derbyScroll = Math.min(maxS, derbyScroll + 60)); }
  R(0, H - 44, W, 44, UI.blueDD); R(0, H - 44, W, 2, '#ffffff');
  button(10, H - 36, 70, 18, 'BACK', () => menu = 'minigames');
  if (derbyPick) { textb(derbyPick.name, W / 2, H - 38, '#fff', 8, 'center', W - 200); textb(`CON ${derbyPick.contact}   POW ${derbyPick.power}   ${derbyPick.bats === 'L' ? 'BATS LEFT' : 'BATS RIGHT'}`, W / 2, H - 25, UI.ice, 7, 'center', W - 200); }
  else textb('TAP A HITTER', W / 2, H - 30, UI.ice, 8, 'center');
  button(W - 96, H - 36, 86, 22, 'START', () => { if (derbyPick) derbyStart(derbyPick); }, derbyPick ? '#2f6fe0' : '#161b26');
}
