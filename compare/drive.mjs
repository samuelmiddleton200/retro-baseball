// usage: node drive.mjs <url> <out.png> <w> <h> <dsf> "<js to run after load>" <waitms>
import { spawn } from 'node:child_process'; import fs from 'node:fs';
const [url, out, W, H, DSF, js, wait] = process.argv.slice(2);
const chrome = ['C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'].find(p => fs.existsSync(p));
const port = 9400 + Math.floor(Math.random()*300);
const p = spawn(chrome, ['--headless=new','--remote-debugging-port='+port,'--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--hide-scrollbars','--user-data-dir='+process.env.TEMP+'/rbprof'+port,'--window-size='+W+','+H,'about:blank'],{stdio:'ignore'});
const sleep = ms => new Promise(r => setTimeout(r, ms));
let tabs; for (let i=0;i<60;i++){ try { tabs = await (await fetch('http://127.0.0.1:'+port+'/json')).json(); if (tabs.find(t=>t.type==='page')) break; } catch(e){} await sleep(250); }
const ws = new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
let id = 0; const pend = {}; ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pend[d.id]) pend[d.id](d); };
const send = (method, params={}) => new Promise(r => { const i=++id; pend[i]=r; ws.send(JSON.stringify({id:i,method,params})); });
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride',{width:+W,height:+H,deviceScaleFactor:+DSF,mobile:false});
const logs=[]; ws.addEventListener('message', m => { const d=JSON.parse(m.data); if (d.method==='Runtime.exceptionThrown') logs.push('EXC '+JSON.stringify(d.params.exceptionDetails.exception?.description||d.params.exceptionDetails.text).slice(0,300)); });
await send('Page.navigate',{url}); await sleep(3500);
if (js) { const r = await send('Runtime.evaluate',{expression:js,awaitPromise:true,returnByValue:true}); if (r.result?.exceptionDetails) logs.push('JS '+JSON.stringify(r.result.exceptionDetails.exception?.description||'').slice(0,300)); else if (r.result?.result?.value !== undefined) console.log('result:', JSON.stringify(r.result.result.value).slice(0,400)); }
await sleep(+wait||1500);
const shot = await send('Page.captureScreenshot',{format:'png'}); fs.writeFileSync(out, Buffer.from(shot.result.data,'base64'));
console.log(logs.length ? logs.join('\n') : 'no errors'); ws.close(); p.kill();
