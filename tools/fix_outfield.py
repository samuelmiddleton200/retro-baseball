"""Outfield of plate_clean.png: replace the repeating chevron grass band and the hatched warning track with smooth, non-repeating grass and dirt."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
rng = np.random.default_rng(7)
a = np.array(Image.open('assets/fields/plate_clean_v2.png').convert('RGB')).astype(float); H, W, _ = a.shape
r, g, b = a[..., 0], a[..., 1], a[..., 2]
dirt = (r > g + 22) & (r > 120)
grass = (g > r + 6) & (g > b + 20)
Y0, Y1 = 148, 262
# the warning track: the dirt pixels between the outfield grass and the infield grass in those rows
track = np.zeros((H, W), bool); track[Y0:Y1] = dirt[Y0:Y1]
track = ndi.binary_closing(track, iterations=2)
# the grass band above the track (and above the infield): green pixels in the rows above each column's first track pixel
top = np.full(W, Y1)
for x in range(W):
    ys = np.where(track[:, x])[0]
    if len(ys): top[x] = ys[0]
band = np.zeros((H, W), bool)
for x in range(W): band[Y0:max(Y0, top[x] - 1), x] = grass[Y0:max(Y0, top[x] - 1), x] | ~dirt[Y0:max(Y0, top[x] - 1), x]
# smooth non-repeating grass: a base colour, wide soft mowing stripes, and fine grain
base = np.array([73, 124, 54.])
xs = np.arange(W)[None, :].repeat(H, 0); ys = np.arange(H)[:, None].repeat(W, 1)
stripe = np.sin(xs / 38.0 + ys * .015) * 3.2 + np.sin(xs / 91.0) * 2.0
grain = ndi.gaussian_filter(rng.normal(0, 1, (H, W)), .8) * 5.5
tex = base[None, None, :] + (stripe + grain)[..., None] * np.array([.8, 1.1, .6])
# a little fade toward the wall so it sits in the light
tex = tex * (.93 + .07 * np.clip((ys - Y0) / 30.0, 0, 1))[..., None]
soft = ndi.gaussian_filter(band.astype(float), .7)[..., None]
a = a * (1 - soft) + tex * soft
# the track: smooth the hatching, keep its colour, add gentle grain
m = ndi.gaussian_filter(track.astype(float), .6)[..., None]
sm = np.stack([ndi.median_filter(a[..., c], size=5) for c in range(3)], -1)
sm = sm + ndi.gaussian_filter(rng.normal(0, 1, (H, W)), 1.0)[..., None] * 3.0
a = a * (1 - m) + sm * m
# the lawn between the track and the plate: keep only its broad mowing stripes (low-pass of the grass alone), drop the tiled chevrons, add fine grain
r2, g2, b2 = a[..., 0], a[..., 1], a[..., 2]
lawn = (g2 > r2 + 8) & (g2 > b2 + 22); lawn[:190] = False; lawn[395:] = False; lawn[:, :4] = False
lawn[:, 740:] = False                                  # the swing button's edge
lawn = ndi.binary_erosion(lawn, iterations=2)
w = lawn.astype(float)
lo = np.stack([ndi.gaussian_filter(a[..., c] * w, 9) / np.maximum(ndi.gaussian_filter(w, 9), 1e-3) for c in range(3)], -1)
grain2 = ndi.gaussian_filter(rng.normal(0, 1, (H, W)), .8) * 4.5
fan = np.sin(((xs - 387.0) / np.maximum(ys - 120.0, 40.0)) * 17.0) * 4.2       # broad mowing stripes fanning out from home
new = lo + fan[..., None] * np.array([.8, 1.1, .6]) + grain2[..., None] * np.array([.8, 1.1, .6])
sf = ndi.gaussian_filter(lawn.astype(float), 1.0)[..., None]
a = a * (1 - sf) + new * sf
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save('assets/fields/plate_clean.png'); print('ok', int(band.sum()), int(track.sum()))
