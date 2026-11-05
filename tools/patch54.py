import re
s = open('index.html', encoding='utf-8').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)
HR_FIRE = r"""
// ── the home run's fire: a pixel flame for a home run under 450 ft, a blue inferno for 450 ft and more ──
function hrFire(S, P){
  const T = S.trail, n = T.length, L = Math.min(110, n - 1), pts = [];
  for (let k = 0; k <= L; k++) pts.push(P(...T[n - 1 - k]));
  while (pts.length < 125) pts.push(pts[pts.length - 1]);
  const h = pts[0], tm = performance.now() / 1000, far = !!S.hrFar;
  const clampf = (x, a, b) => Math.max(a, Math.min(b, x));
  const PT = (x, y, s, c, a) => { g.globalAlpha = clampf(a == null ? 1 : a, 0, 1); const sz = Math.max(1, Math.round(s)); R(Math.round(x - sz / 2), Math.round(y - sz / 2), sz, sz, c); };
  let seed = (Math.floor(tm * 18) * 9301 + 49297) % 233280; const rr = () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  const pal = far ? ['#f0ffff', '#9be9ff', '#2f9bff', '#1d4fd0', '#142a70'] : ['#fffbd0', '#ffd23f', '#ff8a1c', '#d93a14', '#6a1a10'];
  const ramp = u => pal[Math.min(pal.length - 1, Math.max(0, Math.floor(u * pal.length)))];
  for (let k = L; k >= 0; k--){
    const a = k / L, p = pts[k], cnt = a < .15 ? 2 : 4;
    for (let j = 0; j < cnt; j++){
      const u = Math.min(.999, a * .9 + rr() * .3), x = p.x + (rr() - .5) * (2 + 10 * a), y = p.y - a * 10 * rr() - (rr() - .5) * (2 + 3 * a);
      PT(x, y, a < .1 ? 3 : 1 + Math.pow(1 - a, 1.2) * 4 * (.5 + rr()), ramp(u), clampf(1 - a * .9, .1, 1) * (j ? .7 : 1));
    }
    if (k % 5 === 0 && rr() < .7) PT(p.x + (rr() - .5) * 12, p.y - a * 18 - rr() * 5, 1, pal[1], 1 - a);
  }
  PT(h.x, h.y, 16, pal[2], .2); PT(h.x, h.y, 11, pal[1], .3); PT(h.x, h.y, 7, pal[0], .65);
  if (far) for (let i = 0; i < 12; i++){ const p = pts[Math.floor(rr() * 60)]; PT(p.x + (rr() - .5) * 18, p.y + (rr() - .5) * 12, 1, '#f0ffff', .9); }
  g.globalAlpha = 1;
}
"""
rep("function gxOverlay(S){", HR_FIRE + "function gxOverlay(S){")
# no thin line for a home run: the fire is the path
rep("  if (S.trail && S.trail.length > 1){                                // the ball's path: a thin white line",
    "  if (S.trail && S.trail.length > 1 && !S.hr){                                // the ball's path: a thin white line")
a = s.index("  if (S.hr && S.trail && S.trail.length > 3){\n    // fire: hottest at the ball")
b = s.index("  if (S.land){", a)
s = s[:a] + "  if (S.hr && S.trail && S.trail.length > 3) hrFire(S, P);\n" + s[b:]
rep("S.hr = !!B.hr; S.hrOut = !!(hi && hi.out);", "S.hr = !!B.hr; S.hrOut = !!(hi && hi.out); S.hrFar = (B.carry || 0) >= 450;")
# a home run has to clear the fence by a clear margin: the wall is 8.5 ft, so 11 ft over it
rep("CONTACT_H: 3, FENCE_H: 9, WALL_BOUNCE: 0.35,", "CONTACT_H: 3, FENCE_H: 11, WALL_BOUNCE: 0.35,       // FENCE_H: a ball has to be this high (ft) at the wall to be a home run; the fence itself is 8.5 ft")
s = s.replace("BUILD = '11-07i'", "BUILD = '11-07j'"); s = re.sub(r"gl3d\.js\?v=11-07i", "gl3d.js?v=11-07j", s)
open('index.html', 'w', encoding='utf-8').write(s)
m = re.findall(r'<script>(.*?)</script>', s, re.S)
open(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/main.js', 'w', encoding='utf-8').write(max(m, key=len))
print('ok')
