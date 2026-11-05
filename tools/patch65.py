s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80]); s = s.replace(a, b)

i = s.index("      if (af < rf){\n        const legLen = fb === 3 ? 127.28 : 90;")
j = s.index("    throwTo(1, tr);\n    if (a1 < t1){ B.play = 'groundout'")
new = """      if (af < rf){                                                              // the force at the lead base can be made: always try for two
        const pv = stepOn ? c : route(fb, tr).catcher, here = bases[fb - 1];
        const pvArm = pv ? pv.armFps : (fb === 4 ? throwFps(((fldTeam().lineup[7]) || c.man).fielding) : c.armFps);
        const pvGo = af + (stepOn ? CFG.PIVOT * .5 : CFG.PIVOT);                // the pivot man catches it, turns and throws
        let pick = null;
        for (const n of [1, 2, 3]){                                              // the other forced men: the batter at first, the runners on the way to second / third
          if (n >= fb && n !== 1) continue;
          let rn = n === 1 ? t1 : null;
          if (n > 1){ if (!M.bases.slice(0, n - 1).every(Boolean)) continue; rn = runTime(spdOf(M.bases[n - 2]), 90); }      // forced: everybody behind him is on
          const len = Math.hypot(here[0] - bases[n - 1][0], here[1] - bases[n - 1][1]), t0 = pvGo + len * CFG.GLOVE_PER_FT;
          const men = (FLD || []).filter(f => f !== c && f !== pv && BAG_COVER[n - 1].includes(f.pos));
          let catcher = null, ct = 99;
          men.forEach(f => { const D = Math.max(0, Math.hypot(f.d - STAND[n][0], f.lat - STAND[n][1]) - .5), tt = fldReach(f, D) + .12; if (tt < ct){ ct = tt; catcher = f; } });
          if (!catcher) continue;
          const arr = Math.max(t0 + len / pvArm, ct);
          if (!pick || rn - arr > pick.margin) pick = { n, arr, t0, len, margin: rn - arr, catcher };      // whoever he has the better chance of getting
        }
        if (pick){
          B.dpBase = fb; B.dp2 = pick.n; putOut(); B.runN = 1; B.out = true;
          B.thr.legs.push({ from:here, to:bases[pick.n - 1], t0:Math.min(pick.t0, pick.arr), t1:pick.arr, len:pick.len }); B.thr.t1 = pick.arr; B.thr.to = bases[pick.n - 1];
          B.thr.pivot = pv; B.thr.catcher = pick.catcher;
          B.play = pick.margin > 0 ? 'dp' : 'fc'; B.tEnd = pick.arr + .6;
          return;
        }
      }
    }
"""
s = s[:i] + new + s[j:]

# bookkeeping: whoever was put out, the rest of the forced men move up
a = s.index("    case 'dp':     st.ab++; out = 2;"); b = s.index("    case 'groundout': case 'flyout': case 'lineout':")
s = s[:a] + """    case 'dp': case 'fc': { st.ab++;
      const fb = (BALL && BALL.dpBase) || 2, outBags = res === 'dp' ? [fb, (BALL && BALL.dp2) || 1] : [fb];      // the bags (1 = the batter at first) where somebody was put out
      out = outBags.length;
      const bs = M.bases, nb = [null, null, null], tot = M.outs + out; let chain = true;
      for (let i = 0; i < 3; i++){
        if (!bs[i]){ chain = false; continue; }
        if (!chain){ nb[i] = bs[i]; continue; }                                                           // not forced: he stays
        const bag = i + 2;
        if (outBags.includes(bag)) continue;
        if (bag >= 4){ if (tot < 3){ score(bs[i]); runs++; } } else nb[bag - 1] = bs[i];
      }
      if (!outBags.includes(1)) nb[0] = M.batter;
      M.bases = nb;
      txt = res === 'dp' ? 'DOUBLE PLAY' : "FIELDER'S CHOICE"; break; }
""" + s[b:]
s = s.replace("BUILD = '11-11g'", "BUILD = '11-11h'").replace("gl3d.js?v=11-11g", "gl3d.js?v=11-11h")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
