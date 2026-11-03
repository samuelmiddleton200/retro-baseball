"""Writes embed.js: the sprites that get recoloured (gp/*, portraits/*) as data: URIs. When index.html is opened straight from a folder (file://),
Chrome treats every image file as a different origin and refuses to let the game read its pixels, so the team colours cannot be applied; images that come
from data: URIs are always readable. index.html loads embed.js only for file:// pages."""
import base64, glob, os
out = ['window.EMB = {']
for p in sorted(glob.glob('assets/gp/*.png') + glob.glob('assets/portraits/*.png')):
    key = p.replace(os.sep, '/')
    out.append('%r:%r,' % (key, 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()))
out.append('};')
open('embed.js', 'w').write('\n'.join(out))
print('embed.js', round(os.path.getsize('embed.js') / 1e6, 2), 'MB')
