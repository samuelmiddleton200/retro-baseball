"""Draw a spinning pixel-art baseball: a lit sphere with curved red seams rotating about the horizontal axis (backspin), 8 frames per size.
Writes assets/ball/spin<N>.png, an atlas of 8 NxN frames side by side, with hard alpha and a 6-colour palette."""
import numpy as np
from PIL import Image

SIZES = [5, 6, 7, 8, 10, 12, 16, 20, 24]
FRAMES = 8
SS = 8                                                     # supersampling per pixel
PAL = {                                                    # rim, white, light grey, grey, seam red, dark seam
    'rim': (38, 43, 64), 'w': (250, 247, 238), 'lg': (226, 222, 216), 'g': (184, 182, 190), 'red': (214, 55, 44), 'dred': (150, 32, 38)}
PAL_ARR = np.array(list(PAL.values()), float)
NAMES = list(PAL.keys())
L = np.array([-.45, -.55, .70]); L /= np.linalg.norm(L)    # light from the top left, toward the viewer

from scipy.spatial import cKDTree
def seam_points(N=6000, A=.42, B=.42):
    t = np.linspace(0, 4 * np.pi, N, endpoint=False)
    th = np.pi / 2 - (np.pi / 2 - B) * np.cos(t); ph = t / 2 + A * np.sin(2 * t)           # the standard baseball-seam curve
    return np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], 1)
SEAM = seam_points()
def rot_x(a): c, s = np.cos(a), np.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def rot_z(a): c, s = np.cos(a), np.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

def render(n, ang):
    m = n * SS
    ys, xs = np.mgrid[0:m, 0:m]
    x = (xs + .5) / m * 2 - 1; y = (ys + .5) / m * 2 - 1
    rr = x * x + y * y; inside = rr <= 1.0
    z = np.sqrt(np.clip(1 - rr, 0, 1))
    P = SEAM @ (rot_x(ang) @ rot_z(.5)).T                       # seam in view space (screen x right, y down, z toward us), tilted a little, then spun
    P = P[P[:, 2] > -.05]
    tree = cKDTree(P[:, :2])
    d, _ = tree.query(np.stack([x.ravel(), y.ravel()], 1)); d = d.reshape(m, m)
    w = .115 + .03 * (1 - z)                                      # seams look thinner near the edge of the ball
    on_seam = (d < w) & inside
    # little stitch ticks across the seam
    shade = np.clip((x * L[0] + y * L[1] + z * L[2]), 0, 1)
    col = np.ones((m, m), int)
    col[shade < .62] = 2
    col[shade < .30] = 3
    col[on_seam] = 4
    col[on_seam & (shade < .42)] = 5
    col[inside & (rr > .76)] = 0
    return col, inside

def frame(n, ang):
    col, inside = render(n, ang)
    out = np.zeros((n, n, 4), np.uint8)
    for j in range(n):
        for i in range(n):
            blk = col[j * SS:(j + 1) * SS, i * SS:(i + 1) * SS]; ins = inside[j * SS:(j + 1) * SS, i * SS:(i + 1) * SS]
            if ins.mean() < .5: continue
            vals = blk[ins]
            cnt = np.bincount(vals, minlength=6)
            k = int(np.argmax(cnt))
            if cnt[4] + cnt[5] >= .28 * len(vals): k = 4 if cnt[4] >= cnt[5] else 5          # seam wins a pixel if it covers a third of it
            if cnt[0] >= .5 * len(vals): k = 0
            out[j, i, :3] = PAL_ARR[k]; out[j, i, 3] = 255
    return out

for n in SIZES:
    atlas = np.zeros((n, n * FRAMES, 4), np.uint8)
    for f in range(FRAMES):
        atlas[:, f * n:(f + 1) * n] = frame(n, f * (2 * np.pi / FRAMES))     # half a turn: the seam repeats every 180 degrees
    Image.fromarray(atlas).save(f'assets/ball/spin{n}.png')
# preview: three sizes x 8 frames, enlarged
prev = Image.new('RGBA', (8 * 12 * 8 + 40, 3 * 12 * 8 + 40), (70, 120, 60, 255)); y = 8
for n in (12, 16, 24):
    a = Image.open(f'assets/ball/spin{n}.png'); a = a.resize((a.width * 4, a.height * 4), Image.NEAREST); prev.alpha_composite(a, (8, y)); y += a.height + 8
prev.save(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/spin_prev.png')
small = Image.new('RGBA', (8 * 14 * 6, 7 * 14 * 6 // 2 + 20), (70, 120, 60, 255)); y = 6
for n in (5, 6, 7, 8, 10):
    a = Image.open(f'assets/ball/spin{n}.png'); a = a.resize((a.width * 6, a.height * 6), Image.NEAREST); small.alpha_composite(a, (8, y)); y += a.height + 6
small.save(r'C:/Users/samue/AppData/Local/Temp/claude/C--Users-samue/edcf540e-0bc8-4ced-b2bb-81aee2de483c/scratchpad/spin_small.png')
print('ok')
