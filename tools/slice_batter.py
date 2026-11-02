"""Cut a ChatGPT figure sheet (4 columns x 2 rows, same figure in 8 poses, white background, magenta kit) into one transparent
PNG per frame, all on a COMMON canvas with the feet at the bottom centre, so the frames can be swapped in place.

usage: python tools/slice_batter.py <sheet.png> <out prefix, e.g. assets/gp/batter> [colors]
"""
import sys, os, json
from collections import deque
import numpy as np
from PIL import Image
try:
    from scipy import ndimage as ndi
except ImportError:
    ndi = None

sheet, prefix = sys.argv[1], sys.argv[2]
COLORS = int(sys.argv[3]) if len(sys.argv) > 3 else 160
raw = Image.open(sheet); has_alpha = raw.mode == 'RGBA' and (np.array(raw)[..., 3] < 20).mean() > .3
im = raw.convert('RGB'); a = np.array(im); H, W, _ = a.shape
COLS, ROWS = 4, 2

if has_alpha:                                                       # the sheet already has a transparent background
    fg = np.array(raw)[..., 3] > 110
else:
    # background = near-white connected to the sheet's edge (white gloves / soles inside the figure survive)
    white = (a[..., 0] > 236) & (a[..., 1] > 236) & (a[..., 2] > 236)
    bg = np.zeros((H, W), bool); q = deque()
    for x in range(W):
        for y in (0, H - 1):
            if white[y, x] and not bg[y, x]: bg[y, x] = True; q.append((y, x))
    for y in range(H):
        for x in (0, W - 1):
            if white[y, x] and not bg[y, x]: bg[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and white[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True; q.append((ny, nx))
    fg = ~bg

# group the pieces of each figure (bat, hands, body) by which grid cell their centre falls in
if ndi is None: raise SystemExit('scipy is needed for labelling: pip install scipy')
lab, n = ndi.label(ndi.binary_dilation(fg, iterations=7))
frames = [np.zeros((H, W), bool) for _ in range(COLS * ROWS)]
for i in range(1, n + 1):
    m = lab == i
    ys, xs = np.where(m & fg)
    if len(ys) < 400: continue                                     # specks
    cx, cy = xs.mean(), ys.mean()
    f = min(ROWS - 1, int(cy // (H / ROWS))) * COLS + min(COLS - 1, int(cx // (W / COLS)))
    frames[f] |= (m & fg)

crops = []
for f, m in enumerate(frames):
    ys, xs = np.where(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    # feet: the horizontal middle of the lowest 10% of the figure
    low = ys > y1 - (y1 - y0) * .10
    px = float(xs[low].mean())
    rgba = np.dstack([a, (m * 255).astype(np.uint8)])[y0:y1, x0:x1]
    crops.append((rgba, px - x0, y1 - y0, x1 - x0))
left = max(c[1] for c in crops); right = max(c[3] - c[1] for c in crops); tall = max(c[2] for c in crops)
CW, CH = int(round(left + right)) + 4, int(tall) + 4
os.makedirs(os.path.dirname(prefix) or '.', exist_ok=True)
sizes = []
for f, (rgba, pivx, h, w) in enumerate(crops):
    canvas = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    canvas.paste(Image.fromarray(rgba, 'RGBA'), (int(round(left - pivx)) + 2, CH - h - 2))
    q8 = canvas.quantize(colors=COLORS, method=Image.FASTOCTREE, dither=Image.NONE)
    out = f'{prefix}{f}.png'; q8.save(out, optimize=True)
    sizes.append(os.path.getsize(out))
    print(out, canvas.size, 'figure px ~', int((np.array(canvas)[..., 3] > 0).sum()))
json.dump({'w': CW, 'h': CH, 'pivotX': CW / 2, 'frames': COLS * ROWS}, open(prefix + '.json', 'w'))
print('canvas', CW, 'x', CH, '| total', round(sum(sizes) / 1e6, 2), 'MB')
