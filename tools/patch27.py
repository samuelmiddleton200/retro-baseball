s = open('index.html', encoding='utf-8').read()

def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)

rep("""  const crowd = S.people; S.people = [];                           // the people are the target's own sprites, drawn over the 3D park below
  GL3D.frame(S);
  g.imageSmoothingEnabled = false; g.drawImage(GX.c, 0, 0, GX.c.width, GX.c.height, 0, 0, W, H);
  gxSprites(crowd, B);""",
"""  const crowd = S.people; S.people = [];                           // the people are the target's own sprites, drawn over the park
  gxParkBG(S);                                                      // the stadium and the camera never change: it is rendered ONCE, then only copied
  g.imageSmoothingEnabled = false; g.drawImage(GX.bg, 0, 0, GX.bg.width, GX.bg.height, 0, 0, W, H);
  gxOverlay(S);                                                     // the ball, its shadow and its path, drawn flat on top
  gxSprites(crowd, B);""")

rep("// the target's sprites in the park: they bob, lean into a run and face the way they go\n", '''// The high view has a fixed camera and a fixed stadium, so rendering the whole 3D scene every frame (the thing that dropped the game to 20 fps when a
// ball was hit) is pure waste: render it once into a picture and copy that.
function gxParkBG(S){
  const key = S.parkKey + '|' + GX.c.width + 'x' + GX.c.height;
  if (GX.bg && GX.bgKey === key) return;
  GL3D.frame({ park:S.park, parkKey:S.parkKey, parkCols:S.parkCols, view:'air', scale:2.4, zone:false, people:[], ball:null, trail:null, time:0 });
  GX.bg = GX.bg || document.createElement('canvas'); GX.bg.width = GX.c.width; GX.bg.height = GX.c.height;
  GX.bg.getContext('2d').drawImage(GX.c, 0, 0); GX.bgKey = key;
}
function gxOverlay(S){
  GL3D.setView('air'); GL3D.placeCamera(); GL3D.cam.updateMatrixWorld(true);
  const P = (x, y, z) => GL3D.toScreen(x, y, z, W, H);
  if (S.trail && S.trail.length > 1){                                // the ball's path: a thin white line
    g.strokeStyle = 'rgba(255,255,255,.55)'; g.lineWidth = .9; g.beginPath();
    S.trail.forEach((t, i) => { const q = P(t[0], t[1], t[2]); i ? g.lineTo(q.x, q.y) : g.moveTo(q.x, q.y); });
    g.stroke();
  }
  if (S.ball){
    const b = S.ball, gq = P(b.x, .05, b.z), q = P(b.x, b.y, b.z), hh = clamp(b.y / 60, 0, 1);
    g.fillStyle = 'rgba(20,14,6,.32)'; g.beginPath(); g.ellipse(gq.x, gq.y, 1.8 + hh * 1.2, .8 + hh * .4, 0, 0, 7); g.fill();    // its shadow on the grass
    g.fillStyle = '#262b40'; g.beginPath(); g.arc(q.x, q.y, 1.5, 0, 7); g.fill();                                                    // dark rim
    g.fillStyle = '#ffffff'; g.beginPath(); g.arc(q.x, q.y, 1.05, 0, 7); g.fill();
  }
}
// the target's sprites in the park: they bob, lean into a run and face the way they go
''')

# the warm-up builds the same picture
rep("    gxSize(); S.view = 'air'; S.scale = 2.4; S.zone = false; S.people = [];\n    GL3D.frame(S);", "    gxSize(); gxParkBG(S);")
s = s.replace("BUILD = '11-02x'", "BUILD = '11-02y'")
open('index.html', 'w', encoding='utf-8').write(s)
print('ok')
