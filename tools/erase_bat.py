"""Erase the extra (diagonal) bat from frame 6 of batter_sheet5: only pixels within a thin band round that bat's own line that are
not the kit's magenta, not skin-pink and not white."""
import sys, numpy as np
from PIL import Image
sheet, out = sys.argv[1], sys.argv[2]
a = np.array(Image.open(sheet).convert('RGB')).astype(int)
ox, oy, sc = 384, 512, 2                       # frame 6 (row 2, col 2) crop origin, shown at 2x
p0 = np.array([125., 150.]) / sc + [ox, oy]    # bat knob
p1 = np.array([350., 330.]) / sc + [ox, oy]    # where the barrel goes behind the shoulder
H, W, _ = a.shape
yy, xx = np.mgrid[0:H, 0:W]
d = p1 - p0; L2 = d @ d
t = np.clip(((xx - p0[0]) * d[0] + (yy - p0[1]) * d[1]) / L2, 0, 1)
dist = np.hypot(xx - (p0[0] + t * d[0]), yy - (p0[1] + t * d[1]))
r, g, b = a[..., 0], a[..., 1], a[..., 2]
white = (r > 232) & (g > 232) & (b > 232)
magenta = (r > 120) & (b > 90) & (g < r * .62) & (g < b * .8)
band = (dist < 27) & (xx < 384 + 345 / sc + 1) & (yy < 512 + 336 / sc)         # about 17 px each side of the line, stop short of the body
kill = band & ~white & ~magenta
a[kill] = 255
print('erased', int(kill.sum()))
Image.fromarray(a.astype(np.uint8)).save(out)
Image.fromarray(a.astype(np.uint8)).crop((384, 512, 768, 1024)).resize((768, 1024)).save(out.replace('.png', '_f6.png'))
