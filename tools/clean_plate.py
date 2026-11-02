"""Clean the people-free field picture (assets/fields/plate_raw.png) -> plate_clean.png.
The raw picture was patched together where the target's players were removed: the outfield dirt arc is a
collage of slices with different vertical offsets, the mound is split by a seam, and behind home plate there is
a green wedge and a blurred smear. This repaints those three areas in the picture's own colours."""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, random
random.seed(7); np.random.seed(7)
im = Image.open('assets/fields/plate_raw.png').convert('RGB'); W, H = im.size
a = np.array(im)

# 1) outfield band: tile one clean slice (mirrored every other time, feathered) across the full width
Y0, Y1 = 150, 218
SX0, SX1 = 408, 478
sl = a[Y0:Y1, SX0:SX1].copy(); sw = SX1 - SX0
out = a.copy()
x = 0; flip = False
while x < W:
    t = sl[:, ::-1] if flip else sl
    wdt = min(sw, W - x)
    out[Y0:Y1, x:x + wdt] = t[:, :wdt]
    x += sw; flip = not flip
# feather the seams a touch so the repeat is not a hard line
for sx in range(sw, W, sw):
    for d in range(-2, 3):
        xx = sx + d
        if 1 <= xx < W - 1:
            out[Y0:Y1, xx] = ((out[Y0:Y1, xx - 1].astype(int) + out[Y0:Y1, xx + 1].astype(int)) // 2).astype(np.uint8)
# the dirt arc is drawn, not copied: its top edge rises toward centre field, it is thickest at the sides
grass_up = out[Y0:176].copy(); grass_dn = out[196:Y1].copy()       # clean grass rows from the tiled slice
dirt_c = np.array([196, 126, 70], float)
for xx in range(W):
    u = ((xx - 380) / 380.0) ** 2
    top = int(round(176 + 11 * u)); bot = int(round(190 + 32 * u))
    for yy in range(Y0, Y1):
        if yy < top: out[yy, xx] = grass_up[(yy - Y0) % grass_up.shape[0], xx]
        elif yy <= bot:
            f = (yy - top) / max(1, bot - top)
            n = ((xx * 7 + yy * 13) % 11 - 5) * 1.6
            c = dirt_c * (1.0 - .16 * f) + n
            if yy == top: c = c * .55 + np.array([40, 70, 30]) * .45          # soft dark lip where dirt meets grass
            out[yy, xx] = np.clip(c, 0, 255)
        else: out[yy, xx] = grass_dn[(yy - bot - 1) % grass_dn.shape[0], xx]
a = out

# 2) behind home plate: dirt, no green wedge, no smear
box = a[430:470, 70:200].reshape(-1, 3).mean(0)                    # the batter's-box dirt colour, so it blends in
bx0, bx1, by0, by1 = 230, 545, 348, 492
reg = np.zeros((by1 - by0, bx1 - bx0, 3))
noise = np.random.normal(0, 6, reg.shape[:2])
for yy in range(reg.shape[0]):
    t = yy / reg.shape[0]
    reg[yy, :, :] = box * (1.0 + .06 * (1 - t) - .05 * t)
reg += noise[..., None]
mimg = Image.new('L', (bx1 - bx0, by1 - by0), 0); md = ImageDraw.Draw(mimg)
md.polygon([(92, 4), (bx1 - bx0 - 92, 4), (bx1 - bx0 - 18, by1 - by0), (18, by1 - by0)], fill=255)
mimg = mimg.filter(ImageFilter.GaussianBlur(9))
m = np.array(mimg, float)[..., None] / 255
a[by0:by1, bx0:bx1] = (a[by0:by1, bx0:bx1] * (1 - m) + np.clip(reg, 0, 255) * m).astype(np.uint8)
img = Image.fromarray(a)
dr = ImageDraw.Draw(img)
# home plate itself
cx, cy = 387, 470
dr.polygon([(cx - 9, cy - 5), (cx + 9, cy - 5), (cx + 9, cy + 1), (cx, cy + 7), (cx - 9, cy + 1)], fill=(240, 236, 226), outline=(120, 100, 80))

# the inner chalk of the two batter's boxes (the dirt above covers it): redraw it
chalk = (236, 226, 206)
dr2 = ImageDraw.Draw(img)
for (x0, x1) in [(228, 327), (448, 548)]: dr2.rectangle((x0, 397, x1, 398), fill=chalk)
for xv in (324, 451): dr2.rectangle((xv, 397, xv + 1, 488), fill=chalk)

# 3) the mound: wipe the old one with infield grass, then draw a clean one
g = np.array(img)
patch = g[262:292, 140:240].copy()                 # clean infield grass to borrow
for yy in range(216, 250):
    for xx in range(300, 520):
        pass
mw, mh = 215, 34
tile = np.tile(patch, (2, 3, 1))[:mh, :mw]
mx0, my0 = 300, 214
mm = Image.new('L', (mw, mh), 0); ImageDraw.Draw(mm).ellipse((6, 2, mw - 6, mh - 2), fill=255)
g2 = Image.fromarray(g)
# grass over the old mound, only where it is dirt-coloured
sub = np.array(g2.crop((mx0, my0, mx0 + mw, my0 + mh))).astype(int)
isdirt = (sub[..., 0] > sub[..., 1] + 25)
sub[isdirt] = tile[isdirt]
g2.paste(Image.fromarray(sub.astype(np.uint8)), (mx0, my0))
dm = ImageDraw.Draw(g2)
cxm, cym, rx, ry = 407, 232, 84, 11
for k, col in enumerate([(120, 74, 38), (176, 112, 60), (205, 138, 78), (222, 158, 96)]):
    dm.ellipse((cxm - rx + k * 5, cym - ry + k * 1.2 - 1, cxm + rx - k * 5, cym + ry - k * 1.6), fill=col)
dm.rectangle((cxm - 9, cym - 2, cxm + 8, cym), fill=(236, 232, 222))                    # the rubber
# the scoreboard panel: take the blank one from idle.png (the picture with its text removed), because the game draws
# its own live score on top and the baked-in LAD/BOS text would show through as doubled digits
idle = Image.open('assets/fields/idle.png').convert('RGB')
g2.paste(idle.crop((0, 0, 232, 100)), (0, 0))
g2.save('assets/fields/plate_clean.png'); print('wrote plate_clean.png')
