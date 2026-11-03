s = open('index.html', encoding='utf-8').read()
g3 = open('gl3d.js', encoding='utf-8').read()

def rep(a, b, cnt=1, src='s'):
    global s, g3
    t = s if src == 's' else g3
    assert t.count(a) == cnt, (t.count(a), a[:80])
    t = t.replace(a, b)
    if src == 's': s = t
    else: g3 = t

# ── the stands: two decks of 50 ft each behind the fence ──
rep("""  strip([[1.5, wallH + .2], [40, wallH + 9]], crowdMat, 96, 12);                        // the seats rising away from the wall
  strip([[40, wallH + 9], [40, wallH + 13]], basic(0x203a40), 1, 1);                    // the rail
  strip([[40, wallH + 13], [84, wallH + 30]], crowdMat, 96, 12);                        // a second, higher section
  strip([[84, wallH + 30], [84, wallH + 36]], basic(0x1f3a3a), 1, 1);                   // back wall
  strip([[84, wallH + 36], [88, wallH + 37]], basic(0x2f5a52), 1, 1);                   // its cap""",
"""  strip([[1.5, wallH + .2], [50, wallH + 26]], crowdMat, 96, 12);                       // the lower deck: 50 ft deep behind the fence
  strip([[50, wallH + 26], [50, wallH + 30]], basic(0x203a40), 1, 1);                   // the rail between the decks
  strip([[50, wallH + 30], [100, wallH + 60]], crowdMat, 96, 12);                       // the upper deck: another 50 ft
  strip([[100, wallH + 60], [100, wallH + 66]], basic(0x1f3a3a), 1, 1);                 // back wall: past it is out of the park
  strip([[100, wallH + 66], [104, wallH + 67]], basic(0x2f5a52), 1, 1);                 // its cap""", src='g')

# ── how high the seats are at a distance beyond the fence, and when a ball is gone ──
rep("function wallDist(angle){", """// the stands behind the fence: lower deck 0-50 ft, upper deck 50-100 ft, then the back wall (the ball is out of the park). Heights in ft, same as gl3d.js
const standH = b => b <= 0 ? 8.5 : b <= 50 ? 8.7 + 25.8 * b / 50 : b <= 100 ? 38.5 + 30 * (b - 50) / 50 : 74.5;
function hrState(B){
  if (!B.hr) return null;
  if (!B.hrInfo){
    const w = wallDist(B.sa), beyond = (B.carry || 0) - w;
    B.hrInfo = { w, beyond, deck: beyond <= 50 ? 1 : beyond <= 100 ? 2 : 3, out: beyond > 100 };
  }
  if (!B.gone){                                                         // once it hits the seats or leaves the park it is not drawn any more
    const r = Math.hypot(B.d, B.lat), now = r - wallDist(Math.atan2(B.lat, B.d) * 180 / Math.PI);
    if (now > 0 && (B.h <= standH(now) || now >= 100)) B.gone = true;
  }
  return B.hrInfo;
}
function wallDist(angle){""")

# ── gxPlay: the ball and its fire vanish when it is gone; the fire is blue when it goes out ──
rep("  S.ball = ballHeld && !B.hr ? null :", "  const hi = hrState(B);\n  S.ball = (ballHeld && !B.hr) || B.gone ? null :")
rep("S.trail = GX.trail.slice(); S.trailMode = 'line'; S.hr = !!B.hr;", "S.trail = B.gone ? [] : GX.trail.slice(); S.trailMode = 'line'; S.hr = !!B.hr; S.hrOut = !!(hi && hi.out);")
# overlay: colours
rep("    g.strokeStyle = S.hr ? 'rgba(255,120,30,.35)' : 'rgba(255,255,255,.55)';", "    g.strokeStyle = S.hr ? (S.hrOut ? 'rgba(80,170,255,.4)' : 'rgba(255,120,30,.35)') : 'rgba(255,255,255,.55)';")
rep("      const col = a < .15 ? '#fffbd0' : a < .35 ? '#ffd23f' : a < .6 ? '#ff8a1c' : a < .82 ? '#d9341a' : '#5a2a28';",
    "      const col = S.hrOut ? (a < .15 ? '#f0ffff' : a < .35 ? '#9be9ff' : a < .6 ? '#2f9bff' : a < .82 ? '#1d4fd0' : '#1c2a5a') : (a < .15 ? '#fffbd0' : a < .35 ? '#ffd23f' : a < .6 ? '#ff8a1c' : a < .82 ? '#d9341a' : '#5a2a28');")
rep("R(Math.round(q.x + (Math.random() - .5) * 9), Math.round(q.y - a * 14 - Math.random() * 4), 1, 1, '#ffd23f'); }", "R(Math.round(q.x + (Math.random() - .5) * 9), Math.round(q.y - a * 14 - Math.random() * 4), 1, 1, S.hrOut ? '#9be9ff' : '#ffd23f'); }")
# banner
rep("    tt('HOME RUN!', W / 2, ty(108), sz, flick ? '#ffffff' : '#ffd23f', 'center');",
    "    const outP = B.hrInfo && B.hrInfo.out;\n    tt(outP ? 'OUT OF THE PARK!' : 'HOME RUN!', W / 2, ty(108), outP ? sz * .78 : sz, flick ? '#ffffff' : outP ? '#7fd0ff' : '#ffd23f', 'center');")
rep("g.fillStyle = `rgba(255,200,40,${.18 * clamp(1 - Math.max(0, T - 2.4) / .8, 0, 1) * e})`;", "g.fillStyle = `rgba(${B.hrInfo && B.hrInfo.out ? '60,150,255' : '255,200,40'},${.18 * clamp(1 - Math.max(0, T - 2.4) / .8, 0, 1) * e})`;")
s2 = s
s = s.replace("BUILD = '11-03v'", "BUILD = '11-03w'")
open('index.html', 'w', encoding='utf-8').write(s)
open('gl3d.js', 'w', encoding='utf-8').write(g3)
import re
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
