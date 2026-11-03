"""Last pass over plate_clean.png (run after build_plate.py and finish_plate.py): removes the remaining glitches.
 - leftover dirt tongues in the infield lawn near third and first base, and the brown streak left of the mound
 - dotted chalk fragments at the start of the left foul line
 - the picture's edge columns (stretched debris along the left and right edges: stands, pause button side, beside first base)
 - the baked red/blue team stripe inside the scoreboard panel that peeks out from under the game's own scoreboard
 - thicker batter's-box chalk (same weight as the runners' white path)
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

a = np.array(Image.open('assets/fields/plate_clean.png').convert('RGB')).astype(float)
H, W, _ = a.shape
r, g, b = a[..., 0], a[..., 1], a[..., 2]

# 1) dirt that wandered into the infield lawn: for each column, the main warning track is the big dirt blob; any dirt-coloured pixels just under it are strays
dirt = (r > g + 18) & (r > 120)
lab, n = ndi.label(dirt[150:262])
sizes = ndi.sum(np.ones_like(lab), lab, range(1, n + 1))
main = lab == (1 + int(np.argmax(sizes)))
cols = list(range(8, 110)) + list(range(660, 748))
yb = {}
for x in cols:
    ys = np.where(main[:, x])[0]
    yb[x] = 150 + ys.max() if len(ys) else None
for seg in (list(range(8, 110)), list(range(660, 748))):
    vals = np.array([yb[x] if yb[x] is not None else np.nan for x in seg], float)
    sm = ndi.median_filter(np.nan_to_num(vals, nan=np.nanmedian(vals)), size=21, mode='nearest')      # the track's lower edge, with the tongues sanded off
    for x, y0, ys_ in zip(seg, vals, sm):
        if np.isnan(y0): continue
        for y in range(int(round(ys_)) + 1, int(y0) + 16):
            if y < H - 20 and a[y, x, 0] > a[y, x, 1] - 14 and a[y + 18, x, 1] > a[y + 18, x, 0] + 8:   # brownish, with clean lawn below it
                a[y, x] = a[y + 18, x]
# the pale tan lip at the track's lower edge near third base: repaint with the track's own colour from higher up the same column
for x in range(20, 58):
    for y in range(212, 227):
        rr, gg, bb = a[y, x]
        if rr > gg + 8 and bb > 66 and gg > 120 and rr > 170 and (rr - bb) < 150:
            a[y, x] = a[203, x]
# the brown streak left of the mound: replace with lawn from just to its left
for y in range(232, 250):
    for x in range(286, 340):
        rr, gg, bb = a[y, x]
        if rr > gg - 12 and not (x > 322 and 226 <= y <= 244 and rr > gg + 20):         # leave the mound's own rim alone
            a[y, x] = a[y, x - 46]

# 2) dotted chalk fragments before the left foul line begins
for y in range(262, 300):
    for x in range(0, 52):
        if a[y, x, 0] > 200 and a[y, x, 1] > 190 and a[y, x, 2] > 160 and (x < 42 or y < 285):
            a[y, x] = a[y, x] * 0 + np.array([174., 110., 62.])

# 3) the edge columns: the game stretches the outer few columns across wide screens, so they must be clean.
#    Stands and sky: clone / mirror (nothing diagonal there). The field: CONTINUE the foul line and lawn edge in the same direction off the screen
#    (mirroring them made a corner), by sliding the dirt below the foul line along its own slope.
a[49:150, 0:14] = a[49:150, 232:246]                                  # left: clone clean stands and wall from beside the scoreboard
for k in range(24): a[54:150, 736 + k] = a[54:150, 735 - k]           # right stands: mirror
for k in range(14): a[:54, 746 + k] = a[:54, 745]                      # (sky beside the pause button: repeat the clean sky)

def lawn_bottom(x):                                                    # first dirt row below the lawn, scanning down from the lawn, for column x
    for y in range(262, 440):
        if a[y, x, 0] > a[y, x, 1] + 25 and a[y + 3, x, 0] > a[y + 3, x, 1] + 25: return y
    return None
def slope(xs):
    pts = [(x, lawn_bottom(x)) for x in xs if lawn_bottom(x) is not None]
    return np.polyfit([p[0] for p in pts], [p[1] for p in pts], 1)[0]
mR = slope(range(690, 733)); mL = slope(range(30, 90))                 # about -0.47 on the right, +0.5 on the left
src = a.copy()
for k in range(1, 25):                                                 # right edge, columns 735+k
    x = 735 + k; yb = lawn_bottom(735) + mR * k
    for y in range(150, H):
        sy = y if y <= yb else y - mR * k                              # below the foul line: slide along its slope
        sy = int(round(min(H - 1, max(0, sy)))); a[y, x] = src[sy, 735]
for k in range(1, 15):                                                 # left edge, columns 14-k
    x = 14 - k; yb = lawn_bottom(14) - mL * k
    for y in range(150, H):
        sy = y if y <= yb else y + mL * k
        sy = int(round(min(H - 1, max(0, sy)))); a[y, x] = src[sy, 14]
# the chalk of the left foul line: it began part-way across the screen as a few dots. Draw it from the very edge, same direction, thinning to a point.
ch = [(x, y) for y in range(262, 330) for x in range(52, 140) if a[y, x, 0] > 215 and a[y, x, 1] > 205 and a[y, x, 2] > 175]
fm, fc = np.polyfit([p[0] for p in ch], [p[1] for p in ch], 1)
for x in range(0, 70):
    w = 0.6 + (x / 70.0) * 1.6                                         # a hair at the edge, filling out to the line's own width
    yc = fm * x + fc
    for y in range(int(yc - 3), int(yc + 4)):
        d = abs(y + .5 - yc)
        if d <= w / 2 + .2:
            t = max(0.0, min(1.0, (w / 2 + .5 - d)))
            a[y, x] = a[y, x] * (1 - t) + np.array([242., 236., 222.]) * t

# 4) the picture's own scoreboard panel carried a red/blue team stripe at its left edge; the game draws its own, so wipe it out
for y in range(26, 70):
    a[y, 16:25] = a[y, 25]

# 5) batter's box chalk as thick as the runners' white path
img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(img); CH = (242, 236, 222)
for p, q in [((225, 397), (326, 397)), ((325, 397), (325, H)), ((226, 397), (176, H - 1)),
             ((449, 397), (549, 397)), ((450, 397), (450, H)), ((548, 397), (606, H - 1))]:
    d.line([p, q], fill=CH, width=4)
img.save('assets/fields/plate_clean.png')
print('polished')
