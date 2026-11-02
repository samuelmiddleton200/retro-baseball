"""Rebuild assets/fields/plate_clean.png from the untouched plate_clean_v1.png with crisp edges and no smears:
 1. outfield grass band + warning track: smooth, non-repeating (tools/fix_outfield.py logic)
 2. infield lawn: broad mowing stripes only, hard edges
 3. home dirt: procedural grain over the original broad shading, hard edges, left batter's box chalk mirrored from the right one
"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
rng = np.random.default_rng(11)
a = np.array(Image.open('assets/fields/plate_clean_v1.png').convert('RGB')).astype(float); H, W, _ = a.shape
xs = np.arange(W)[None, :].repeat(H, 0).astype(float); ys = np.arange(H)[:, None].repeat(W, 1).astype(float)
def chans(): return np.array([.8, 1.1, .6])
r, g, b = a[..., 0], a[..., 1], a[..., 2]
chalk0 = (r > 205) & (g > 195) & (b > 165)
dirt0 = (r > g + 22) & (r > 110) & ~chalk0
grass0 = (g > r + 6) & (g > b + 20)

# ── left batter's box: wipe the smear, copy the right box's chalk across ──
BX0, BX1, BY0 = 100, 330, 380
a[BY0:, BX0:BX1] = np.array([176, 112, 62.])
chalkR = chalk0[BY0:, 775 - BX1:775 - BX0][:, ::-1]
colR = a.copy(); colR[BY0:, BX0:BX1] = np.array(Image.open('assets/fields/plate_clean_v1.png').convert('RGB'))[BY0:, 775 - BX1:775 - BX0][:, ::-1]
a[BY0:, BX0:BX1][chalkR] = colR[BY0:, BX0:BX1][chalkR]
r, g, b = a[..., 0], a[..., 1], a[..., 2]
chalk = (r > 205) & (g > 195) & (b > 165)
# the swing button and the scoreboard are overdrawn by the game; leave their rectangles alone
keep = np.zeros((H, W), bool); keep[345:, 650:] = True; keep[:110] = True

# ── outfield band and track ──
dirt = (r > g + 22) & (r > 110) & ~chalk
grass = (g > r + 6) & (g > b + 20)
Y0, Y1 = 148, 262
track = np.zeros((H, W), bool); track[Y0:Y1] = dirt[Y0:Y1]; track = ndi.binary_closing(track, iterations=2)
top = np.full(W, Y1)
for x in range(W):
    yy = np.where(track[:, x])[0]
    if len(yy): top[x] = yy[0]
band = np.zeros((H, W), bool)
for x in range(W): band[Y0:max(Y0, top[x] - 1), x] = True
stripe = np.sin(xs / 38.0 + ys * .015) * 3.2 + np.sin(xs / 91.0) * 2.0
grain = ndi.gaussian_filter(rng.normal(0, 1, (H, W)), .8) * 5.5
tex = np.array([73, 124, 54.])[None, None, :] + (stripe + grain)[..., None] * chans()
tex *= (.93 + .07 * np.clip((ys - Y0) / 30.0, 0, 1))[..., None]
a[band] = tex[band]
sm = np.stack([ndi.median_filter(a[..., c], size=5) for c in range(3)], -1) + ndi.gaussian_filter(rng.normal(0, 1, (H, W)), 1.0)[..., None] * 3.0
a[track] = sm[track]

# ── infield lawn: broad stripes only; the outer 3 px keep their original pixels so the edge stays crisp ──
lawn = grass0.copy(); lawn[:190] = False; lawn[395:] = False; lawn[:, 740:] = False
lawn = ndi.binary_opening(lawn, iterations=1)
core = ndi.binary_erosion(lawn, iterations=3)
w = lawn.astype(float)
lo = np.stack([ndi.gaussian_filter(a[..., c] * w, 9) / np.maximum(ndi.gaussian_filter(w, 9), 1e-3) for c in range(3)], -1)
fan = np.sin(((xs - 387.0) / np.maximum(ys - 120.0, 40.0)) * 17.0) * 4.2
new = lo + fan[..., None] * chans() + (ndi.gaussian_filter(rng.normal(0, 1, (H, W)), .8) * 4.5)[..., None] * chans()
a[core] = new[core]

# ── home dirt: hard-edged mask, broad shading kept, fine grain added ──
r, g, b = a[..., 0], a[..., 1], a[..., 2]
chalk = (r > 205) & (g > 195) & (b > 165)
dd = (r > g + 22) & (r > 110) & ~chalk; dd[:250] = False; dd &= ~keep
wd = dd.astype(float)
lod = np.stack([ndi.gaussian_filter(a[..., c] * wd, 5) / np.maximum(ndi.gaussian_filter(wd, 5), 1e-3) for c in range(3)], -1)
gr = ndi.gaussian_filter(rng.normal(0, 1, (H, W)), .7) * 4.0
nd = lod + gr[..., None]
a[dd] = nd[dd]
# the soft smear above the plate: snap the grass/dirt edge to a clean line (no blended pixels)
zone = np.zeros((H, W), bool); zone[340:376, 290:480] = True
mix = zone & ~dd & ~grass0 & ~chalk
a[mix] = a[mix] * 0 + np.array([172, 108, 60.]) + gr[mix][:, None]
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save('assets/fields/plate_clean.png'); print('built')
