"""Second pass over plate_clean.png (after build_plate.py): foul ground to clean dirt, hand-drawn crisp chalk for both batter's boxes,
and a hard, tidy grass/dirt edge above the plate. No blur anywhere."""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
rng = np.random.default_rng(5)
im = Image.open('assets/fields/plate_clean.png').convert('RGB'); a = np.array(im).astype(float); H, W, _ = a.shape
xs = np.arange(W)[None, :].repeat(H, 0).astype(float); ys = np.arange(H)[:, None].repeat(W, 1).astype(float)
grain = ndi.gaussian_filter(rng.normal(0, 1, (H, W)), .7) * 4.0
DIRT = np.array([174, 110, 62.])
def dirt_at(m, shade=0.0): a[m] = DIRT + shade + grain[m][:, None] * np.array([1, .8, .6])
bright_pre = (a[..., 0] > 190) & (a[..., 1] > 175) & (a[..., 2] > 140)
# 1) foul ground: below the left/right foul lines it is plain dirt (the old picture had smeared green wedges there)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
green = (g > r - 16)
left = (ys > 268 + .52 * xs + 3) & (xs < 262) & (ys > 262) & green
rt = (ys > 283 + (760 - xs) * .467 + 3) & (xs > 515) & (ys > 262) & green & ~((xs >= 650) & (ys >= 345) & (xs < 748))
dirt_at(left); dirt_at(rt)
flat = np.zeros((H, W), bool); flat[400:, :140] = True; flat[400:, 640:] = True; flat &= ~((xs >= 650) & (ys >= 345) & (xs < 748)); dirt_at(flat & ~bright_pre)
# wipe every old chalk fragment in the box areas, then draw the chalk properly
box = np.zeros((H, W), bool); box[385:, 140:330] = True; box[385:, 440:660] = True
bright = (a[..., 0] > 190) & (a[..., 1] > 175) & (a[..., 2] > 140)
dirt_at(box & bright)
# smooth the leftover pale haze in the boxes: any pixel lighter than dirt there becomes dirt
haze = box & (a[..., 0] > 200)
dirt_at(haze)
# 2) crisp chalk
img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img); CH = (242, 236, 222)
def line(p, q, w=2): d.line([p, q], fill=CH, width=w)
line((225, 397), (326, 397)); line((325, 397), (325, H)); line((226, 397), (176, H - 1))        # left box
line((449, 397), (549, 397)); line((450, 397), (450, H)); line((548, 397), (606, H - 1))        # right box
a = np.array(img).astype(float)
# 3) the grass/dirt edge above the plate: one clean line, grass above, dirt below
ye = lambda x: 358 - 7 * np.clip(1 - ((x - 392) / 95.0) ** 2, 0, 1)
zone = np.zeros((H, W), bool); zone[335:380, 290:490] = True
edge = ye(xs)
grassz = zone & (ys < edge)
dirtz = zone & (ys >= edge)
src = a[332:336].mean(0)                                   # grass just above, copied down column by column
a[grassz] = src[xs[grassz].astype(int)] + grain[grassz][:, None] * np.array([.8, 1.1, .6])
col = a[386:392].mean(0)
a[dirtz] = col[xs[dirtz].astype(int)] + grain[dirtz][:, None] * np.array([1, .8, .6])
out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); out.save('assets/fields/plate_clean.png'); print('finished')
