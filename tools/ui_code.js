// ── the Retro Basket look: bright blue ground, dark-blue boxes with white edges, chunky yellow buttons ──────────────
const UI = { blue:'#2f5fd8', blueD:'#2149b4', blueDD:'#17348a', navy:'#0f1f55', yellow:'#ffd23f', yellowD:'#c99a12', red:'#e24b3b', green:'#44c45d', ice:'#cfe0ff' };
const uiBg = () => R(0, 0, W, H, UI.blue);
// a box: 2px white edge, corners knocked off by a pixel
function uiBox(x, y, w, h, fill = UI.blueDD){
  R(x + 1, y, w - 2, h, '#ffffff'); R(x, y + 1, w, h - 2, '#ffffff');
  R(x + 2, y + 2, w - 4, h - 4, fill);
}
// big titles: white (or a colour) with a navy drop shadow
function ptitle(s, x, y, size, c = '#ffffff', align = 'center'){
  g.font = `700 ${Math.round(size * .86)}px ${PIXF}`; g.textAlign = align; g.textBaseline = 'top';
  g.fillStyle = UI.navy; g.fillText(s, x | 0, (y + Math.max(2, size * .18)) | 0);
  g.fillStyle = c; g.fillText(s, x | 0, y | 0);
}
const BTN_YELLOW = new Set(['#2f6fe0', '#2a6a3a', '#6a3aa8']);
const BTN_OFF = new Set(['#161b26', '#1a1f2a']);
const BTN_RED = new Set(['#4a2030', '#2a1a1a']);
function button(x, y, w, h, label, fn, col = '#1a2230', tc = '#fff', size = 8){
  const off = BTN_OFF.has(col);
  const kind = off ? 'off' : BTN_YELLOW.has(col) ? 'yellow' : BTN_RED.has(col) ? 'red' : 'box';
  const fs = Math.round(size * .86);
  g.font = `700 ${fs}px ${PIXF}`; g.textAlign = 'center'; g.textBaseline = 'top';
  if (kind === 'box'){
    uiBox(x, y, w, h, col === '#1a2230' || col === '#1a2030' ? UI.blueDD : mix(UI.blueDD, col, .35));
    g.fillStyle = tc; g.fillText(label, (x + w / 2) | 0, (y + (h - fs) / 2) | 0);
  } else {
    const body = kind === 'yellow' ? UI.yellow : kind === 'red' ? UI.red : '#4d525e';
    const dark = kind === 'yellow' ? UI.yellowD : kind === 'red' ? '#9c2f23' : '#383c46';
    R(x + 1, y + 3, w - 2, h - 3, UI.navy); R(x, y + 4, w, h - 5, UI.navy);          // the drop shadow
    R(x + 1, y, w - 2, h - 2, body); R(x, y + 1, w, h - 4, body);
    R(x + 2, y + 1, w - 4, 1, 'rgba(255,255,255,.45)');
    R(x + 1, y + h - 4, w - 2, 2, dark);
    g.fillStyle = kind === 'yellow' ? '#241a00' : kind === 'red' ? '#ffffff' : '#9aa0ad';
    g.fillText(label, (x + w / 2) | 0, (y + (h - 3 - fs) / 2 + 1) | 0);
  }
  btns.push({ x, y, w, h, fn });
}
// a small coin, for prices and the balance
function coinIcon(x, y, r = 4){
  g.fillStyle = UI.yellowD; g.beginPath(); g.arc(x, y + 1, r, 0, 7); g.fill();
  g.fillStyle = UI.yellow; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill();
  g.fillStyle = UI.yellowD; g.fillRect(x - 1, y - r + 2, 2, r * 2 - 3);
}
function coinText(n, x, y, size = 8, c = UI.yellow, align = 'left'){
  const s = n.toLocaleString(), wpx = s.length * size * .62;
  const x0 = align === 'center' ? x - (wpx + size + 4) / 2 : align === 'right' ? x - wpx - size - 4 : x;
  coinIcon(x0 + size / 2, y + size / 2, size * .5);
  text(s, x0 + size + 3, y, c, size);
}
