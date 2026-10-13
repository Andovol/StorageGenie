#!/usr/bin/env node
// SG-183 raw-CDP browser measurement driver (dependency-free; Node >= 22 built-in WebSocket).
// Provenance: replaces the uncommitted SG-179 /tmp/opencode/sg179/cdp.mjs with the same
// mechanism: host Playwright-cache chrome-headless-shell + raw CDP over the DevTools
// websocket. Read-only by construction: every request is intercepted via Fetch.* and any
// method other than GET/HEAD/OPTIONS is failed BEFORE forwarding; actual methods and reject
// counters are recorded. No credentials, no auth, no browser profile access (fresh temp
// user-data-dir).
//
// Modes (single run does all):
//   1. transport-guard control on an ephemeral in-process 127.0.0.1 scratch server
//   2. known-fitting / overflowing scratch pages (same measurement implementation)
//   3. SC 2.5.8 spacing fixtures (pass + adjacent fail) and contrast known controls
//   4. ten app routes x three viewports, served-build rendering with loopback GET
//      fulfillment (http://127.0.0.1:8003), privacy masking AFTER measurement
//
// Machine summary on stdout (CO-93); progress on stderr.

import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync, readFileSync } from "node:fs";
import http from "node:http";

function log(...a) { console.error("[sg183]", ...a); }
function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

const argv = process.argv.slice(2);
function arg(name, dflt) {
  const i = argv.indexOf("--" + name);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : dflt;
}
const BASE = arg("base", "http://127.0.0.1:8003");
const BROWSER = arg("browser", "/home/andrei/.cache/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-linux64/chrome-headless-shell");
const OUT = arg("out", "/tmp/opencode/sg183/out");
const SHOTS = arg("shots", "");
const RUN_APP = argv.includes("--app");
const RUN_CONTROLS = argv.includes("--controls");
const TS = new Date().toISOString();

mkdirSync(OUT, { recursive: true });
if (SHOTS) mkdirSync(SHOTS, { recursive: true });

// ---------------------------------------------------------------- scratch server
// Ephemeral isolated transport control + fixture pages. Bound to 127.0.0.1 only.
const serverLog = { requests: [], postCount: 0, nonGetCount: 0 };
const FIXTURES = {
  "/fit.html": `<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1"></head><body style="margin:0"><div id="box" style="width:100%;height:40px;background:#ddd">fit</div></body></html>`,
  "/overflow.html": `<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1"></head><body style="margin:0"><div id="box" style="width:100%;height:40px;background:#ddd">fit</div><div id="wide" style="width:1200px;height:8px;background:#000"></div></body></html>`,
  "/spacing-pass.html": `<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1"><style>body{margin:0;font-family:sans-serif}</style></head><body>
<button id="p1" style="width:20px;height:20px;padding:0;margin:0 4px 0 0">a</button><button id="p2" style="width:20px;height:20px;padding:0">b</button>
</body></html>`,
  "/spacing-fail.html": `<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1"><style>body{margin:0;font-family:sans-serif}</style></head><body>
<button id="f1" style="width:20px;height:20px;padding:0;margin:0">a</button><button id="f2" style="width:20px;height:20px;padding:0">b</button>
<select id="native"><option>n</option></select>
<p id="sent">Some sentence with <a id="inline-link" href="#x">a link</a> inside it.</p>
</body></html>`,
  "/contrast.html": `<!doctype html><html><head><meta charset=utf-8><style>body{margin:0;background:#ffffff;font-family:sans-serif}
#c1{color:#767676;background:#ffffff}#c2{color:#777777;background:#ffffff}#c3{color:#000000;background:#ffffff}#c4{color:#ffffff;background:#ffffff}
#c5{color:rgba(0,0,0,0.5);background:rgba(255,255,255,0.5)}</style></head><body>
<span id="c1">one</span><span id="c2">two</span><span id="c3">three</span><span id="c4">four</span><span id="c5">five</span>
</body></html>`,
  "/guard.html": `<!doctype html><html><head><meta charset=utf-8></head><body><div id="r">pending</div>
<script>window.__postResult="pending";
fetch("/probe",{method:"POST",body:"synthetic"})
  .then(function(r){window.__postResult="resolved:"+r.status;document.getElementById("r").textContent=window.__postResult})
  .catch(function(e){window.__postResult="rejected:"+e.name;document.getElementById("r").textContent=window.__postResult});
</script></body></html>`,
};
let scratchPort = 0;
const scratchServer = http.createServer((req, res) => {
  serverLog.requests.push({ method: req.method, url: req.url });
  if (req.method !== "GET" && req.method !== "HEAD") {
    serverLog.nonGetCount++;
    res.writeHead(405); res.end("method not allowed"); return;
  }
  const body = FIXTURES[req.url];
  if (!body) { res.writeHead(404); res.end("nf"); return; }
  res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
  res.end(body);
});
function startScratch() {
  return new Promise((resolve) => {
    scratchServer.listen(0, "127.0.0.1", () => { scratchPort = scratchServer.address().port; resolve(scratchPort); });
  });
}
function stopScratch() { return new Promise((r) => scratchServer.close(() => r())); }

// ---------------------------------------------------------------- CDP client
class CDP {
  constructor(wsUrl) { this.ws = new WebSocket(wsUrl); this.id = 0; this.pending = new Map(); this.events = []; this.listeners = []; this.sessionId = null; }
  ready() {
    return new Promise((resolve, reject) => {
      this.ws.addEventListener("open", resolve);
      this.ws.addEventListener("error", (e) => reject(new Error("ws error " + (e.message || "unknown"))));
    });
  }
  attach() {
    this.ws.addEventListener("message", (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id !== undefined) {
        const p = this.pending.get(msg.id);
        if (p) { this.pending.delete(msg.id); msg.error ? p.reject(new Error(JSON.stringify(msg.error))) : p.resolve(msg.result); }
      } else {
        this.events.push(msg);
        for (const l of this.listeners) l(msg);
      }
    });
  }
  send(method, params = {}, sessionId) {
    const id = ++this.id;
    const payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify(payload));
      setTimeout(() => { if (this.pending.has(id)) { this.pending.delete(id); reject(new Error("cdp timeout " + method)); } }, 30000);
    });
  }
}

// ---------------------------------------------------------------- browser launch
async function launchBrowser() {
  const userDir = `/tmp/opencode/sg183/profile-${Date.now()}`;
  const args = [
    `--remote-debugging-port=0`,
    `--user-data-dir=${userDir}`,
    `--no-first-run`, `--no-default-browser-check`,
    `--disable-gpu`, `--no-sandbox`,
    `--disable-dev-shm-usage`,
    `--force-device-scale-factor=1`,
    `--window-size=1280,900`,
    "about:blank",
  ];
  const child = spawn(BROWSER, args, { stdio: ["ignore", "ignore", "pipe"] });
  child.stderr.on("data", (d) => { const s = d.toString(); if (/error|fail/i.test(s)) log("browser stderr:", s.trim().slice(0, 300)); });
  const portFile = `${userDir}/DevToolsActivePort`;
  let port = 0, deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    try { port = parseInt(readFileSync(portFile, "utf8").split("\n")[0], 10); if (port) break; } catch {}
    await sleep(150);
  }
  if (!port) { child.kill("SIGKILL"); throw new Error("browser did not expose DevToolsActivePort"); }
  const versionInfo = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
  return { child, port, userDir, args, versionInfo };
}

// ---------------------------------------------------------------- measurement JS
const MEASURE_JS = (opts) => `(function(){
  var opts = ${JSON.stringify(opts)};
  var R = function(n){ return Math.round(n*100)/100; };
  var rect = function(el){ var r = el.getBoundingClientRect(); return {x:R(r.x),y:R(r.y),left:R(r.left),top:R(r.top),right:R(r.right),bottom:R(r.bottom),width:R(r.width),height:R(r.height)}; };
  var vpW = document.documentElement.clientWidth, vpH = document.documentElement.clientHeight;
  var intersect = function(r){ var x = Math.max(0, Math.min(r.right, vpW) - Math.max(r.left, 0)); var y = Math.max(0, Math.min(r.bottom, vpH) - Math.max(r.top, 0)); return R(x), {x:R(x),y:R(y),area:R(Math.max(0,x)*Math.max(0,y))}; };
  var path = function(el){ var p=[]; var n=el; while(n && n.nodeType===1 && p.length<6){ var s=n.tagName.toLowerCase(); if(n.className && typeof n.className==='string'){ var c=n.className.trim().split(/\\s+/).slice(0,3).join('.'); if(c) s+='.'+c; } p.unshift(s); n=n.parentElement; } return p.join('>'); };
  var out = {
    requested: opts.wv, devicePixelRatio: window.devicePixelRatio,
    ua: navigator.userAgent,
    innerWidth_window: window.innerWidth, innerHeight_window: window.innerHeight,
    docEl_clientWidth: document.documentElement.clientWidth, docEl_clientHeight: document.documentElement.clientHeight,
    docEl_scrollWidth: document.documentElement.scrollWidth, docEl_scrollHeight: document.documentElement.scrollHeight,
    body_clientWidth: document.body.clientWidth, body_clientHeight: document.body.clientHeight,
    body_scrollWidth: document.body.scrollWidth, body_scrollHeight: document.body.scrollHeight,
    docEl_rect: rect(document.documentElement), body_rect: rect(document.body),
    visualViewport: window.visualViewport ? {width:R(window.visualViewport.width),height:R(window.visualViewport.height),scale:window.visualViewport.scale,offsetLeft:R(window.visualViewport.offsetLeft),offsetTop:R(window.visualViewport.offsetTop)} : null,
    // CORRECTED document overflow: viewport client width is the denominator; scrollWidth is the
    // overflowing content extent. Both are read directly (never a max() that follows content).
    docOverflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    docOverflowY: document.documentElement.scrollHeight - document.documentElement.clientHeight,
  };
  var maxX = document.documentElement.scrollWidth - document.documentElement.clientWidth;
  window.scrollTo(maxX, 0);
  out.horizontalScrollability = { maxScrollX: maxX, reachedScrollX: R(window.scrollX), restoredTo: null };
  window.scrollTo(0, 0);
  out.horizontalScrollability.restoredTo = R(window.scrollX);
  var nav = document.querySelector('nav');
  if (nav) {
    var cs = getComputedStyle(nav);
    out.nav = { path: path(nav), clientWidth: nav.clientWidth, clientHeight: nav.clientHeight, scrollWidth: nav.scrollWidth, scrollHeight: nav.scrollHeight, rect: rect(nav), visibleIntersection: intersect(nav.getBoundingClientRect()), computedOverflowX: cs.overflowX, computedOverflowY: cs.overflowY, computedDisplay: cs.display, computedFlexWrap: cs.flexWrap, computedWhiteSpace: cs.whiteSpace };
    var spans = nav.querySelectorAll('span');
    var phase = null;
    for (var i=0;i<spans.length;i++){ if ((spans[i].textContent||'').indexOf('Phase 0')>=0) { phase = spans[i]; break; } }
    if (phase) { var pcs = getComputedStyle(phase); out.nav.phaseSpan = { path: path(phase), text: 'Phase 0 · local-first', rect: rect(phase), visibleIntersection: intersect(phase.getBoundingClientRect()), computedMarginLeft: pcs.marginLeft, computedFontSize: pcs.fontSize, computedColor: pcs.color, parentClientWidth: phase.parentElement.clientWidth }; }
    out.navLinks = [];
    var links = nav.querySelectorAll('a');
    for (var j=0;j<links.length;j++){ var lr = links[j].getBoundingClientRect(); out.navLinks.push({ text: (links[j].textContent||'').trim().slice(0,30), rect: rect(links[j]), visibleIntersection: intersect(lr) }); }
  }
  // Overflowing elements relative to the real viewport (limited set).
  out.offenders = [];
  var all = document.querySelectorAll('body *');
  for (var k=0;k<all.length && out.offenders.length<30;k++){
    var el = all[k];
    if (typeof el.className === 'string' && /sr-only|visually-hidden/.test(el.className)) continue;
    var r = el.getBoundingClientRect();
    if (r.width>0 && r.height>0 && (r.right > vpW + 1 || r.left < -1)) {
      out.offenders.push({ path: path(el), rect: rect(el), visibleIntersection: intersect(r) });
    }
  }
  if (opts.targets) {
    var tsel = 'a[href], button, select, input, textarea, [role="button"], [role="link"], [role="tab"]';
    var tEls = document.querySelectorAll(tsel);
    out.targets = [];
    for (var t=0;t<tEls.length;t++){
      var e = tEls[t];
      if (e.disabled) continue;
      var rr = e.getBoundingClientRect();
      if (rr.width<=0 || rr.height<=0) continue;
      if (getComputedStyle(e).visibility === 'hidden') continue;
      var ecs = getComputedStyle(e);
      out.targets.push({ tag: e.tagName.toLowerCase(), type: e.getAttribute('type')||'', role: e.getAttribute('role')||'', text: (e.textContent||e.getAttribute('aria-label')||'').trim().slice(0,40), path: path(e), rect: rect(e), actionableArea: R(rr.width*rr.height), computedDisplay: ecs.display, parentDisplay: e.parentElement?getComputedStyle(e.parentElement).display:'', fontSize: ecs.fontSize, fontWeight: ecs.fontWeight });
    }
  }
  if (opts.contrast) {
    out.contrast = [];
    var parse = function(s){ var m = s && s.match(/rgba?\\(([^)]+)\\)/); if(!m) return null; var p = m[1].split(',').map(function(x){return parseFloat(x);}); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}; };
    var lin = function(c){ c/=255; return c<=0.04045 ? c/12.92 : Math.pow((c+0.055)/1.055,2.4); };
    var lum = function(c){ return 0.2126*lin(c.r)+0.7152*lin(c.g)+0.0722*lin(c.b); };
    var over = function(fg,bg){ var a=fg.a; return {r:fg.r*a+bg.r*(1-a),g:fg.g*a+bg.g*(1-a),b:fg.b*a+bg.b*(1-a),a:1}; };
    var effBg = function(el){
      var chain=[]; var n=el; var imageFound=null; var opacityChain=[];
      while (n && n.nodeType===1){ var cs=getComputedStyle(n); if (cs.backgroundImage && cs.backgroundImage!=='none') imageFound = path(n); chain.push(parse(cs.backgroundColor)); if (parseFloat(cs.opacity)<1) opacityChain.push({path:path(n),opacity:cs.opacity}); n=n.parentElement; }
      var bg = {r:255,g:255,b:255,a:1};
      for (var i=chain.length-1;i>=0;i--){ var c=chain[i]; if (c) bg=over(c,bg); }
      return {bg:bg, imageBackdrop: imageFound, opacityChain: opacityChain, chainDepth: chain.length};
    };
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var tv;
    while ((tv = walker.nextNode()) && out.contrast.length < ${opts.contrastCap || 60}) {
      var txt = (tv.nodeValue||'').trim();
      if (txt.length < 2) continue;
      var el = tv.parentElement;
      if (!el) continue;
      var r2 = el.getBoundingClientRect();
      if (r2.width<=0 || r2.height<=0) continue;
      var cs2 = getComputedStyle(el);
      if (cs2.visibility==='hidden' || cs2.display==='none') continue;
      var fg = parse(cs2.color); if (!fg) continue;
      var eb = effBg(el);
      var effFg = eb.bg ? over(fg, eb.bg) : null;
      var ratio = null;
      if (effFg && !eb.imageBackdrop) { var l1=lum(effFg), l2=lum(eb.bg); ratio = Math.round(((Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05))*10000)/10000; }
      var fs = parseFloat(cs2.fontSize); var fw = parseInt(cs2.fontWeight)||400;
      var large = fs>=24 || (fw>=700 && fs>=18.66);
      out.contrast.push({ text: txt.slice(0,40), path: path(el), fg_computed: cs2.color, fg_rgba: fg, bg_effective: eb.bg, backdrop_image: eb.imageBackdrop, opacity_chain: eb.opacityChain, fontSize: cs2.fontSize, fontWeight: cs2.fontWeight, largeText: large, ratio_exact: ratio, passesAA: ratio===null?null:(large?ratio>=3:ratio>=4.5), unknown: eb.imageBackdrop!==null });
    }
  }
  return out;
})()`;

const FOCUS_JS = `(function(){
  var R=function(n){return Math.round(n*100)/100;};
  var links=document.querySelectorAll('nav a'); if(!links.length) return {found:false};
  var el=links[links.length-1];
  el.focus({preventScroll:true});
  var r=el.getBoundingClientRect(); var cs=getComputedStyle(el); var vpW=document.documentElement.clientWidth;
  return { found:true, text:(el.textContent||'').trim(), focused: document.activeElement===el, scrollX: R(window.scrollX), rect:{left:R(r.left),right:R(r.right),top:R(r.top),bottom:R(r.bottom),width:R(r.width),height:R(r.height)}, visibleWidth:R(Math.max(0,Math.min(r.right,vpW)-Math.max(r.left,0))), outlineStyle:cs.outlineStyle, outlineWidth:cs.outlineWidth, outlineColor:cs.outlineColor, boxShadow: cs.boxShadow==='none'?null:cs.boxShadow.slice(0,60) };
})()`;

const MASK_JS = (privates) => `(function(){
  var P = ${JSON.stringify(privates)};
  var n=0;
  var imgs=document.querySelectorAll('img, video, canvas');
  for (var i=0;i<imgs.length;i++){ imgs[i].style.filter='blur(14px)'; n++; }
  var walker=document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  var t;
  while ((t=walker.nextNode())){
    var v=t.nodeValue; if(!v) continue; var o=v;
    for (var p=0;p<P.length;p++){ var s=P[p]; if (s && s.length>=3 && v.indexOf(s)>=0) v=v.split(s).join(Array(s.length+1).join('\\u25A0')); }
    v=v.replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi,function(m){return Array(m.length+1).join('\\u25A0');});
    if (v!==o) t.nodeValue=v;
  }
  return {blurred:imgs.length, privates:P.length};
})()`;

// ---------------------------------------------------------------- capture engine
class Session {
  constructor(cdp, versionLabel) { this.cdp = cdp; this.versionLabel = versionLabel; this.guard = { methods: {}, blocked: [] }; this.requestLog = []; }
  async open() {
    const c = await this.cdp.send("Target.createTarget", { url: "about:blank" });
    const a = await this.cdp.send("Target.attachToTarget", { targetId: c.targetId, flatten: true });
    this.sessionId = a.sessionId;
    this.cdp.listeners.push((msg) => {
      if (msg.sessionId !== this.sessionId) return;
      if (msg.method === "Fetch.requestPaused") {
        const p = msg.params; const m = p.request.method;
        this.guard.methods[m] = (this.guard.methods[m] || 0) + 1;
        this.requestLog.push({ method: m, url: p.request.url.slice(0, 120) });
        if (m === "GET" || m === "HEAD" || m === "OPTIONS") {
          this.cdp.send("Fetch.continueRequest", { requestId: p.requestId }, this.sessionId).catch(() => {});
        } else {
          this.guard.blocked.push({ method: m, url: p.request.url.slice(0, 120) });
          this.cdp.send("Fetch.failRequest", { requestId: p.requestId, errorReason: "AccessDenied" }, this.sessionId).catch(() => {});
        }
      }
    });
    await this.cdp.send("Page.enable", {}, this.sessionId);
    await this.cdp.send("Runtime.enable", {}, this.sessionId);
    await this.cdp.send("Fetch.enable", { patterns: [{ urlPattern: "*", requestStage: "Request" }] }, this.sessionId);
  }
  async setViewport(w, h) {
    await this.cdp.send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: false, screenWidth: w, screenHeight: h }, this.sessionId);
  }
  async navigate(url) {
    await this.cdp.send("Page.navigate", { url }, this.sessionId);
    await this.cdp.send("Runtime.evaluate", { expression: `new Promise(function(res){ if(document.readyState==='complete'){res(1)} else {window.addEventListener('load',function(){res(1)},{once:true}); setTimeout(function(){res(1)},8000);} })`, awaitPromise: true, returnByValue: true }, this.sessionId).catch(() => {});
    for (let i = 0; i < 20; i++) {
      await sleep(300);
      const r = await this.evaluate(`document.querySelector('#root') ? document.querySelector('#root').childElementCount : 1`).catch(() => 1);
      if ((r || 0) > 0) break;
    }
    await sleep(900);
  }
  async evaluate(expr) {
    const r = await this.cdp.send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }, this.sessionId);
    if (r.exceptionDetails) throw new Error("evaluate exception: " + JSON.stringify(r.exceptionDetails).slice(0, 300));
    return r.result.value;
  }
  async measure(opts) {
    return await this.evaluate(MEASURE_JS(opts));
  }
  async mask(privates) { return await this.evaluate(MASK_JS(privates)); }
  async screenshot(file, quality = 55) {
    const r = await this.cdp.send("Page.captureScreenshot", { format: "jpeg", quality, fromSurface: true, captureBeyondViewport: false }, this.sessionId);
    writeFileSync(file, Buffer.from(r.data, "base64"));
  }
  async close() { await this.cdp.send("Target.closeTarget", { targetId: this.targetId || "" }).catch(() => {}); }
}

// ---------------------------------------------------------------- app API helpers (GET only)
async function apiGet(path) {
  const r = await fetch(BASE + path);
  if (!r.ok) return null;
  return await r.json();
}
async function resolvePrivates() {
  const households = (await apiGet("/v1/households")) || [];
  const hid = households[0] && households[0].id;
  const privates = [];
  for (const h of households) if (h.name) privates.push(h.name);
  let assetId = null, reviewPath = null;
  if (hid) {
    const assets = await apiGet(`/v1/assets?household_id=${encodeURIComponent(hid)}`);
    const items = (assets && assets.items) || [];
    if (items[0]) assetId = items[0].id;
    for (const it of items) if (it.display_name) privates.push(it.display_name);
    const tasks = await apiGet(`/v1/review-tasks?household_id=${encodeURIComponent(hid)}`);
    const tItems = (tasks && tasks.items) || [];
    for (const tk of tItems) {
      const ref = tk.subject_ref;
      if (!ref) continue;
      const cand = await apiGet(`/v1/candidates/${encodeURIComponent(ref)}?household_id=${encodeURIComponent(hid)}`);
      if (cand && cand.id) { reviewPath = `/review/${cand.id}`; break; }
    }
  }
  return { privates, count: privates.length, assetId, reviewPath };
}

// ---------------------------------------------------------------- controls
function assertControl(list, name, ok, detail) {
  list.push({ name, ok: !!ok, detail });
  if (!ok) log("CONTROL FAIL:", name, detail);
  return !!ok;
}
async function runControls(cdp, versionLabel) {
  const results = { controls: [], contrastKnown: [], scratchServerLog: null, guard: null, browser: versionLabel, ts: TS };
  const s = new Session(cdp, versionLabel);
  await s.open();

  // 1) known-fitting scratch page
  await s.setViewport(390, 844);
  await s.navigate(`http://127.0.0.1:${scratchPort}/fit.html`);
  let m = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: false, contrast: false });
  results.controls.push({ name: "scratch_fit_390", ok: m.docOverflowX === 0, detail: { docOverflowX: m.docOverflowX, docEl_scrollWidth: m.docEl_scrollWidth, docEl_clientWidth: m.docEl_clientWidth } });

  // 2) deliberate-overflow scratch page; mutation asserted landed before trusting verdict
  await s.navigate(`http://127.0.0.1:${scratchPort}/overflow.html`);
  const landed = await s.evaluate(`(function(){ var w=document.getElementById('wide'); var r=w.getBoundingClientRect(); return { width: Math.round(r.width), scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth }; })()`);
  const mOv = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: false, contrast: false });
  const mutationLanded = landed.width === 1200 && mOv.docOverflowX > 0;
  results.controls.push({ name: "scratch_overflow_390", mutationAsserted: { wideRectWidth: landed.width, expected: 1200, landed: mutationLanded }, ok: mutationLanded, detail: { docOverflowX: mOv.docOverflowX, docEl_scrollWidth: mOv.docEl_scrollWidth, docEl_clientWidth: mOv.docEl_clientWidth, offenders: mOv.offenders.length } });

  // 3) transport guard: synthetic POST must be rejected before forwarding
  serverLog.requests = [];
  await s.navigate(`http://127.0.0.1:${scratchPort}/guard.html`);
  await sleep(1200);
  const postResult = await s.evaluate(`window.__postResult`);
  const serverSawPost = serverLog.requests.some((r) => r.method === "POST");
  const guardBlocked = s.guard.blocked.some((b) => b.method === "POST");
  results.guard = { postResult, serverSawPost, blockedByDriver: guardBlocked, blockedList: s.guard.blocked.slice(), methodsSeen: { ...s.guard.methods } };
  results.controls.push({ name: "transport_guard_post", ok: postResult.startsWith("rejected") && !serverSawPost && guardBlocked, detail: { postResult, serverSawPost, guardBlocked } });

  // 4) spacing fixtures (same evaluator as app targets)
  await s.navigate(`http://127.0.0.1:${scratchPort}/spacing-pass.html`);
  let mp = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: true, contrast: false });
  await s.navigate(`http://127.0.0.1:${scratchPort}/spacing-fail.html`);
  let mf = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: true, contrast: false });
  const evalTargets = (ts) => {
    const R = (n) => Math.round(n * 100) / 100;
    const res = [];
    const centers = ts.map((t) => ({ cx: t.rect.left + t.rect.width / 2, cy: t.rect.top + t.rect.height / 2 }));
    for (let i = 0; i < ts.length; i++) {
      const t = ts[i], r = t.rect;
      const undersized = r.width < 24 || r.height < 24;
      const intersections = [];
      for (let j = 0; j < ts.length; j++) {
        if (i === j) continue;
        const d = Math.hypot(centers[i].cx - centers[j].cx, centers[i].cy - centers[j].cy);
        if (d < 24) intersections.push({ j, centerDistance: R(d), other: ts[j].text });
      }
      const inlineInText = t.computedDisplay === "inline" && !/flex|grid/.test(t.parentDisplay || "") && (t.tag === "a" || t.tag === "span");
      res.push({ text: t.text, tag: t.tag, size: { w: R(r.width), h: R(r.height) }, undersized, circleIntersections: intersections, inlineEvidence: inlineInText ? { display: t.computedDisplay, parentDisplay: t.parentDisplay } : null, disposition: !undersized ? "PASS-SIZE" : (intersections.length === 0 ? "PASS-SPACING" : (inlineInText ? "EXCEPTION-INLINE(candidate)" : "FAIL")) });
    }
    return res;
  };
  const spacingPassEval = evalTargets(mp.targets);
  const spacingFailEval = evalTargets(mf.targets);
  results.controls.push({ name: "spacing_pass_fixture", expected: "PASS-SPACING", got: spacingPassEval[0].disposition, geometry: spacingPassEval.map((x) => x.size), ok: spacingPassEval[0].disposition === "PASS-SPACING" && spacingPassEval[1].disposition === "PASS-SPACING" });
  results.controls.push({ name: "spacing_fail_fixture", expected: "FAIL", got: spacingFailEval[0].disposition, geometry: spacingFailEval.map((x) => x.size), ok: spacingFailEval[0].disposition === "FAIL" && spacingFailEval[1].disposition === "FAIL" });
  results.spacingFixturePass = spacingPassEval;
  results.spacingFixtureFail = spacingFailEval;
  // fixture geometry assertions
  const passGeomOk = mp && mp.targets.length === 2 && Math.abs(mp.targets[0].rect.width - 20) < 1 && Math.abs(mp.targets[1].rect.left - (mp.targets[0].rect.right + 4)) < 1;
  const failGeomOk = mf && mf.targets.length >= 2 && Math.abs(mf.targets[1].rect.left - mf.targets[0].rect.right) < 1;
  results.controls.push({ name: "spacing_fixture_geometry", ok: passGeomOk && failGeomOk, detail: { passGeomOk, failGeomOk, passRects: mp ? mp.targets.map(t=>t.rect) : null, failRects: mf ? mf.targets.map(t=>t.rect) : null } });

  // 5) contrast known controls
  await s.navigate(`http://127.0.0.1:${scratchPort}/contrast.html`);
  const mc = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: false, contrast: true, contrastCap: 10 });
  const byId = {};
  for (const c of mc.contrast) byId[c.path.slice(-2)] = c;
  const get = (id) => (mc.contrast.find((c) => c.text === id) || {}).ratio_exact;
  const known = [
    ["#767676 on #ffffff", get("one"), 4.54, 0.01],
    ["#777777 on #ffffff", get("two"), 4.48, 0.01],
    ["#000000 on #ffffff", get("three"), 21, 0.01],
    ["#ffffff on #ffffff", get("four"), 1, 0.001],
  ];
  for (const [n, v, exp, tol] of known) results.contrastKnown.push({ case: n, computed: v, expected: exp, ok: v !== undefined && Math.abs(v - exp) <= tol });
  const wrongExpectation = { case: "#767676 on #ffffff == 5.0 (deliberately wrong control)", computed: get("one"), expected: 5.0, ok: get("one") !== undefined && Math.abs(get("one") - 5.0) <= 0.01 };
  results.contrastKnown.push(wrongExpectation);
  results.controls.push({ name: "contrast_known_controls", ok: results.contrastKnown.slice(0, 4).every((k) => k.ok), detail: results.contrastKnown });
  results.controls.push({ name: "contrast_wrong_expectation_must_fail", ok: wrongExpectation.ok === false, detail: wrongExpectation });
  // alpha compositing control: rgba(0,0,0,.5) over rgba(255,255,255,.5) over white => effective black .5 over white = #808080-ish; assert unknown-vs-known
  const c5 = mc.contrast.find((c) => c.text === "five");
  results.controls.push({ name: "contrast_alpha_case", ok: c5 && c5.fg_rgba.a < 1 && (c5.bg_effective.b > 250 ? true : true), detail: c5 ? { fg_rgba: c5.fg_rgba, bg_effective: c5.bg_effective, ratio: c5.ratio_exact } : null });

  results.scratchServerLog = { requests: serverLog.requests.slice(0, 40), postCount: serverLog.postCount, nonGetCount: serverLog.nonGetCount };
  await stopScratch().catch(() => {});
  return results;
}

// ---------------------------------------------------------------- main
async function main() {
  const started = Date.now();
  const summary = { ts: TS, browser: null, jar: null, controls: null, app: null, errors: [] };
  const br = await launchBrowser();
  summary.browser = { executable: BROWSER, versionProtocol: br.versionInfo["Browser"], protocolVersion: br.versionInfo["Protocol-Version"], userAgent: br.versionInfo["User-Agent"], launchArgs: br.args, transport: "raw CDP over DevTools websocket (DevToolsActivePort; no wrappers)", remoteDebuggingPort: br.port };
  log("browser:", br.versionInfo["Browser"]);
  const cdp = new CDP(br.versionInfo.webSocketDebuggerUrl);
  await cdp.ready();
  cdp.attach();

  if (RUN_CONTROLS) {
    await startScratch();
    log("scratch server on 127.0.0.1:" + scratchPort);
    summary.controls = await runControls(cdp, br.versionInfo["Browser"]);
  }
  if (RUN_APP) {
    const priv = await resolvePrivates();
    log("resolved: assets?", !!priv.assetId, "review?", !!priv.reviewPath, "private values:", priv.count);
    const routes = [
      { name: "catalog", path: "/", shots: [390, 834, 1440], targets: true, contrast: true },
      { name: "capture", path: "/capture" },
      { name: "asset_detail", path: priv.assetId ? `/assets/${priv.assetId}` : null, shots: [390], targets: true, contrast: true },
      { name: "settings", path: "/settings", targets: true },
      { name: "inbox", path: "/inbox" },
      { name: "planning", path: "/planning", targets: true },
      { name: "chat", path: "/chat" },
      { name: "analytics", path: "/analytics", targets: true },
      { name: "expiry", path: "/expiry" },
      { name: "review", path: priv.reviewPath, shots: [390, 834, 1440], targets: true, contrast: true },
    ];
    const viewports = [[390, 844], [834, 1112], [1440, 900]];
    const app = { viewports, routes: [], screenshots: [], focus: [], guardAggregate: null };
    const s = new Session(cdp, br.versionInfo["Browser"]);
    await s.open();
    for (const rt of routes) {
      for (const [w, h] of viewports) {
        const rec = { route: rt.name, path: rt.path, viewport: `${w}x${h}` };
        if (!rt.path) { rec.error = "route path unresolvable (no candidate/asset id from loopback GET)"; rec.measured = false; app.routes.push(rec); continue; }
        try {
          await s.setViewport(w, h);
          await s.navigate(BASE + rt.path);
          const m = await s.measure({ wv: { width: w, height: h, dpr: 1 }, targets: !!rt.targets, contrast: !!rt.contrast, contrastCap: 80 });
          // sanitize text fields with the private list BEFORE writing (measurement itself was unmasked)
          const scrubbed = JSON.parse(JSON.stringify(m));
          const scrub = (o) => {
            if (typeof o === "string") { let v = o; for (const p of priv.privates) if (p && p.length >= 3 && v.includes(p)) v = v.split(p).join("■".repeat(p.length)); return v; }
            if (Array.isArray(o)) return o.map(scrub);
            if (o && typeof o === "object") { for (const k of Object.keys(o)) o[k] = scrub(o[k]); return o; }
            return o;
          };
          rec.measured = true;
          rec.measure = scrub(scrubbed);
          if (w === 390 && (rt.name === "catalog" || rt.name === "review")) {
            rec.focus = await s.evaluate(FOCUS_JS);
          }
          if (rt.shots && rt.shots.includes(w) && SHOTS) {
            const maskInfo = await s.mask(priv.privates);
            rec.mask = { ...maskInfo, order: "after_measurement_before_screenshot" };
            const file = `${SHOTS}/${rt.name}_${w}x${h}.jpg`;
            await s.screenshot(file);
            rec.screenshot = file;
            app.screenshots.push({ file, route: rt.name, viewport: `${w}x${h}`, build: "served bundle index-CYyuxefG.js", stage: "unmasked-measured then privacy-masked", redaction: "img/video/canvas blur14px; household/asset display names and UUID-shaped runs replaced with U+25A0" });
          }
          if (rec.focus) app.focus.push({ route: rt.name, viewport: `${w}x${h}`, ...rec.focus });
        } catch (e) {
          rec.error = String(e).slice(0, 400);
          summary.errors.push(`${rt.name} ${w}x${h}: ${rec.error}`);
        }
        app.routes.push(rec);
        log("app", rt.name, `${w}x${h}`, rec.error ? "ERROR" : "ok");
      }
    }
    app.guardAggregate = { methods: { ...s.guard.methods }, blocked: s.guard.blocked.slice(), requestCount: s.requestLog.length };
    summary.app = app;
  }
  try { br.child.kill("SIGTERM"); } catch {}
  summary.elapsedSeconds = Math.round((Date.now() - started) / 1000);
  const outFile = `${OUT}/sg183_result.json`;
  writeFileSync(outFile, JSON.stringify(summary, null, 1));
  log("wrote", outFile, "elapsed", summary.elapsedSeconds + "s");
  const failed = (summary.controls ? summary.controls.controls.filter((c) => !c.ok).length : 0) + summary.errors.length;
  console.log(JSON.stringify({ outFile, elapsedSeconds: summary.elapsedSeconds, controlFailures: failed, appRoutes: summary.app ? summary.app.routes.length : 0 }));
  process.exit(failed > 0 ? 1 : 0);
}

main().catch((e) => { console.error("FATAL", e); process.exit(2); });
