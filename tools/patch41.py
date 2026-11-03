s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80]); s = s.replace(a, b)

rep("""      if (a2 < r1){ const a1b = a2 + .55 + 127.28 / (c.armFps * .9); if (a1b < t1){ B.play = 'dp'; throwTo(2, tr); B.tEnd = a1b + .6; B.runN = 1; B.out = true; return; } }
    }""", """      if (a2 < r1){
        const a1b = a2 + .55 + 127.28 / (c.armFps * .9);
        if (a1b < t1){                                                        // second, then on to first: a double play (the relay is drawn as a second leg)
          B.play = 'dp'; throwTo(2, tr); B.tEnd = a1b + .6; B.runN = 1; B.out = true;
          B.thr.legs.push({ from:[127.28, 0], to:[63.64, 63.64], t0:a2 + .55, t1:a1b, len:90 }); B.thr.t1 = a1b; B.thr.to = [63.64, 63.64];
          return;
        }
        if (a2 + .3 < r1 && !M.bases[1]){                                      // no double play, but he has the runner at second easily: the force out there, batter safe at first
          B.play = 'fc'; throwTo(2, tr); B.tEnd = a2 + .8; B.runN = 1; B.out = true; return;
        }
      }
    }""")
# every FORCED runner must run on a grounder: the batter is forced to first, so a runner on first is forced to second, and so on up the chain
rep("function applyPlay(res){", """// the runners a ground ball forces to move: first base's runner always, second's if first is taken, third's if first and second are
function forcedAdvance(){
  const b = M.bases; let runs = 0;
  if (!b[0]) return 0;
  if (b[1]){ if (b[2]){ score(b[2]); runs++; } b[2] = b[1]; }
  b[1] = b[0]; b[0] = null;
  return runs;
}
function applyPlay(res){""")
rep("    case 'dp':     st.ab++; out = 2; M.bases[0] = null; txt = 'DOUBLE PLAY'; break;",
    "    case 'dp':     st.ab++; out = 2; M.bases[0] = null; txt = 'DOUBLE PLAY'; break;\n    case 'fc':     st.ab++; out = 1; M.bases[0] = M.batter; txt = \"FIELDER'S CHOICE\"; break;                  // the runner is forced out at second, the batter is on first")
rep("      else txt = res === 'groundout' ? 'GROUND OUT' : res === 'flyout' ? 'FLY OUT' : 'LINE OUT';\n      break;",
    "      else txt = res === 'groundout' ? 'GROUND OUT' : res === 'flyout' ? 'FLY OUT' : 'LINE OUT';\n      if (res === 'groundout' && M.outs + out < 3){ runs += forcedAdvance(); if (runs){ st.rbi += runs; } }      // the batter is out, but the runners he forced move up\n      break;")
# the runners show it: forced runners run on a groundout / fielder's choice / double play
rep("const adv = B.isCatch || B.play === 'groundout' ? 0 : (B.runN || 1); run('run' + i, p2, 90 * (i + 1), manual ? 360 : 90 * (i + 1) + adv * 90); });",
    "const adv = runnerAdv(B, i); run('run' + i, p2, 90 * (i + 1), manual ? 360 : 90 * (i + 1) + adv * 90); });")
rep("    const adv = B.foul || B.isCatch || B.play === 'groundout' ? 0 : (B.runN || 1);", "    const adv = B.foul ? 0 : runnerAdv(B, i);")
rep("// the runners a ground ball forces to move:", """// how many bases the runner who stands on base i (0 = first) goes on this play: on a ground ball the forced ones go one, the others stay
function runnerAdv(B, i){
  if (B.isCatch) return 0;
  if (B.play === 'groundout' || B.play === 'dp' || B.play === 'fc'){ for (let k = 0; k <= i; k++) if (!M.bases[k]) return 0; return 1; }
  return B.runN || 1;
}
// the runners a ground ball forces to move:""")
s = s.replace("BUILD = '11-04o'", "BUILD = '11-04p'")
open('index.html', 'w', encoding='utf-8').write(s)
import re
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
