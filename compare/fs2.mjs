// usage: node fireshots.mjs <variant|none> <outprefix>   (renders a home run at four moments of its flight)
import { spawn } from 'node:child_process'; import fs from 'node:fs';
const [variant, prefix] = process.argv.slice(2);
const chrome = ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'].find(p => fs.existsSync(p));
const port = 9700 + Math.floor(Math.random() * 200);
const p = spawn(chrome, ['--headless=new', '--remote-debugging-port=' + port, '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--hide-scrollbars', '--user-data-dir=' + process.env.TEMP + '/rbfp' + port, '--window-size=1266,585', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let tabs; for (let i = 0; i < 60; i++) { try { tabs = await (await fetch('http://127.0.0.1:' + port + '/json')).json(); if (tabs.find(t => t.type === 'page')) break; } catch (e) {} await sleep(250); }
const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
let id = 0; const pend = {}; ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pend[d.id]) pend[d.id](d); };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async expr => { const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }); if (r.result?.exceptionDetails) console.log('JS ERR', JSON.stringify(r.result.exceptionDetails.exception?.description || r.result.exceptionDetails.text).slice(0, 300)); return r.result?.result?.value; };
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1266, height: 585, deviceScaleFactor: 2, mobile: false });
await send('Page.navigate', { url: 'http://localhost:8788/index.html' }); await sleep(3500);
await ev(`(async()=>{  const r = window.__rb; r.newGame('NYY'); r.startGame(0, false); await new Promise(x => setTimeout(x, 9000));
  r.nextPitch(); r.P.thrown = true; r.phase = 'atbat'; r.launchBall(${variant}, 27, 8, .9); r.P.state = 'inplay'; r.P.playT = 0; r.planFielders(); window.__freeze = true; return r.BALL.hr + ' ' + r.BALL.T; })()`);
const info = await ev(`(()=>{ const B = window.__rb.BALL; return [B.hr, B.T].join(' '); })()`);
console.log('ball', info);
const T = parseFloat(String(info).split(' ')[1]);
const marks = [.03, .07, .11, .16]; const out = [];
for (let mi = 0; mi < marks.length; mi++) {
  await ev(`(async()=>{ const r = window.__rb, B = r.BALL, target = ${marks[mi] * T}; let guard = 0; while (B.t < target && guard++ < 400) { r.stepBall(30); await new Promise(x => requestAnimationFrame(() => requestAnimationFrame(x))); } return B.t; })()`);
  await sleep(120);
  const head = await ev(`window.__headScr || null`);
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(`${prefix}_${mi}.png`, Buffer.from(shot.result.data, 'base64')); out.push(head);
}
fs.writeFileSync(`${prefix}_heads.json`, JSON.stringify(out));
console.log('done', JSON.stringify(out)); ws.close(); p.kill();
