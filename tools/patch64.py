s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80]); s = s.replace(a, b)

# ── double plays: the pivot man is the one who catches at the first base he is sent to; the man who catches at FIRST is somebody else ──
rep("      const fb = M.bases[1] ? (M.bases[2] ? 4 : 3) : 2, fr = M.bases[fb - 2];\n      const af = throwArr(fb, tr), rf = runTime(spdOf(fr), 90);",
    """      let fb = M.bases[1] ? (M.bases[2] ? 4 : 3) : 2;
      // the third baseman who fields it on top of third just steps on the bag himself (the force is there with first and second taken)
      const dS = Math.hypot(pf[0] - 63.64, pf[1] + 63.64), stepOn = c.pos === '3B' && fb >= 3 && dS <= 15;
      if (stepOn) fb = 3;
      const fr = M.bases[fb - 2];
      const af = stepOn ? tf + .15 + dS / (c.speed * CFG.ROUTE_EFF) : throwArr(fb, tr), rf = runTime(spdOf(fr), 90);
      const putOut = () => {                                                         // the ball to the force base: a throw to the man covering it, or the 3B carrying it to third himself
        if (stepOn){ B.thr = mkThr({ legs:[{ from:pf, to:bases[2], t0:tf, t1:af, len:dS }], arr:af, relays:[] }, pf, bases[2]); B.thr.stepOn = true; B.thr.catcher = null; }
        else throwTo(fb, tr);
      };""")
rep("pvT0 = af + CFG.PIVOT + legLen * CFG.GLOVE_PER_FT,", "pvT0 = af + (stepOn ? CFG.PIVOT * .5 : CFG.PIVOT) + legLen * CFG.GLOVE_PER_FT,")
rep("const pv = route(fb, tr).catcher, pvArm = pv ? pv.armFps : c.armFps,", "const pv = stepOn ? c : route(fb, tr).catcher, pvArm = pv ? pv.armFps : c.armFps,")
rep("          B.play = 'dp'; B.dpBase = fb; throwTo(fb, tr); B.tEnd = a1b + .6; B.runN = 1; B.out = true;\n          B.thr.legs.push({ from:bases[fb - 1], to:[63.64, 63.64], t0:pvT0, t1:a1b, len:legLen }); B.thr.t1 = a1b; B.thr.to = [63.64, 63.64];",
    """          B.play = 'dp'; B.dpBase = fb; putOut(); B.tEnd = a1b + .6; B.runN = 1; B.out = true;
          B.thr.legs.push({ from:bases[fb - 1], to:[63.64, 63.64], t0:pvT0, t1:a1b, len:legLen }); B.thr.t1 = a1b; B.thr.to = [63.64, 63.64];
          B.thr.pivot = pv;                                                    // he is at the force base, the man at first is the one who catches the second throw
          B.thr.catcher = FLD.filter(f => f !== c && f !== pv && BAG_COVER[0].includes(f.pos)).sort((x, y) => Math.hypot(x.d - 63.64, x.lat - 63.64) - Math.hypot(y.d - 63.64, y.lat - 63.64))[0] || null;""")
rep("          B.play = 'fc'; B.dpBase = fb; throwTo(fb, tr); B.tEnd = af + .8;", "          B.play = 'fc'; B.dpBase = fb; putOut(); B.tEnd = af + .8;")
rep("  if (pthr && pthr.catcher){ const bi =", "  if (pthr && pthr.pivot && B.dpBase >= 2 && B.dpBase <= 3 && pthr.pivot !== c) send(pthr.pivot, STAND[B.dpBase][0], STAND[B.dpBase][1], B.dpBase);       // the man who turns the double play is on his bag\n  if (pthr && pthr.catcher){ const bi =")
# third baseman who stepped on the bag: the SS does not also go there
rep("    else if (c === third){ bag(first, 1); bag(second, 2); bag(short, 3); }", "    else if (c === third){ bag(first, 1); bag(second, 2); if (B.thr && B.thr.stepOn){ const p = toward(short, { d:STAND[2][0], lat:0 }, .5); send(short, p[0], p[1], 0); } else bag(short, 3); }")
# a force at third with the bases loaded puts the runner from third home when the double play is turned
rep("      if (fb === 4){ b[2] = b[1]; b[1] = b[0]; b[0] = null; }                                  // out at home and at first: the others move up\n      else if (fb === 3){ b[1] = b[0]; b[0] = null; }",
    "      if (fb === 4){ b[2] = b[1]; b[1] = b[0]; b[0] = null; }                                  // out at home and at first: the others move up\n      else if (fb === 3){ if (b[2] && M.outs + 2 < 3){ score(b[2]); runs++; } b[2] = b[1]; b[1] = b[0]; b[0] = null; }")
rep("else if (fb === 3){ b[1] = b[0]; b[0] = M.batter; } else b[0] = M.batter;", "else if (fb === 3){ if (b[2]){ score(b[2]); runs++; } b[2] = b[1]; b[1] = b[0]; b[0] = M.batter; } else b[0] = M.batter;")

# ── a runner on third tags up on a caught fly: the fielder throws home only if he can reach it from where he stands (no relay); otherwise he holds it and the run scores ──
rep("    B.isCatch = true; B.play = B.la > CFG.LINE_MAX_LA ? 'flyout' : 'lineout'; B.tJudge = tf; B.tEnd = tf + 1.0; B.runN = 0; tagOK(); return;",
    """    B.isCatch = true; B.play = B.la > CFG.LINE_MAX_LA ? 'flyout' : 'lineout'; B.tJudge = tf; B.tEnd = tf + 1.0; B.runN = 0; tagOK();
    if (!userBats() && B.play === 'flyout' && M.outs < 2 && M.bases[2]){
      B.sacFly = true;
      const len = Math.hypot(pf[0], pf[1]);
      if (len <= throwRange(c.man.fielding)){                                  // he can reach the plate from here: he throws, and the runner is out if the ball beats him
        const t0 = tf + CFG.TRANSFER_AIR + len * CFG.GLOVE_PER_FT, t1 = t0 + len / c.armFps, runner = tf + runTime(spdOf(M.bases[2]), 90);
        B.thr = mkThr({ legs:[{ from:pf, to:bases[3], t0, t1, len }], arr:t1, relays:[] }, pf, bases[3]); B.thr.catcher = null;
        B.sacOut = t1 < runner; B.tEnd = Math.max(t1, runner) + .8;
      }
    }
    return;""")
rep("      else if (res === 'flyout' && M.bases[2] && M.outs < 2 && chance(.55)){ runs += advance(1, false); st.rbi += runs; st.ab--; st.sf = (st.sf || 0) + 1; txt = 'SAC FLY'; }",
    "      else if (res === 'flyout' && BALL && BALL.sacOut && M.bases[2]){ out = 2; M.bases[2] = null; txt = 'DOUBLE PLAY AT THE PLATE'; }      // thrown out at home\n      else if (res === 'flyout' && M.bases[2] && M.outs < 2 && (BALL && BALL.sacFly || chance(.55))){ runs += advance(1, false); st.rbi += runs; st.ab--; st.sf = (st.sf || 0) + 1; txt = 'SAC FLY'; }")
s = s.replace("BUILD = '11-11f'", "BUILD = '11-11g'").replace("gl3d.js?v=11-11f", "gl3d.js?v=11-11g")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
