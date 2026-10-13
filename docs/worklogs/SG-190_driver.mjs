#!/usr/bin/env node
// SG-190 raw-CDP browser measurement driver (dependency-free; Node >= 22 built-in WebSocket).
// Derived from the audited SG-183 driver (docs/worklogs/SG-183_driver.mjs) with three
// changes: (1) a built-in static SPA server for a scratch candidate/base build, (2) the
// doc-overflow / target-size / contrast receivers unchanged, (3) added normal-Tab focus,
// narrow-menu, sticky-obscuring, draft-preservation and 320px reflow probes.
// Read-only by construction: every request is intercepted via Fetch.* and any method other
// than GET/HEAD/OPTIONS is failed BEFORE forwarding; actual methods and reject counters are
// recorded. No credentials, no auth, no browser profile access (fresh temp user-data-dir).
//
// Modes:
//   --serve <dir> --port <n>   static SPA server (default off)
//   --controls                 scratch fixtures: fitting/overflow, spacing pass/fail,
//                              contrast known controls, transport guard
//   --app                      ten app routes x viewports, screenshots (masked after
//                              measurement), normal-Tab / menu / sticky / draft probes
//
// Machine summary on stdout (CO-93); progress on stderr.

import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync, readFileSync, existsSync, statSync } from "node:fs";
import { extname, join } from "node:path";
import http from "node:http";

function log(...a) { console.error("[sg190]", ...a); }
function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

const argv = process.argv.slice(2);
function arg(name, dflt) {
  const i = argv.indexOf("--" + name);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : dflt;
}
const BASE = arg("base", "http://127.0.0.1:8003");
const API_ORIGIN = arg("api-origin", "http://localhost:8003");
const BROWSER = arg("browser", "/home/andrei/.cache/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-linux64/chrome-headless-shell");
const OUT = arg("out", "/tmp/opencode/sg190/out");
const SHOTS = arg("shots", "");
const SERVE_DIR = arg("serve", "");
const PORT = parseInt(arg("port", "8010"), 10);
const RUN_APP = argv.includes("--app");
const RUN_CONTROLS = argv.includes("--controls");
const TS = new Date().toISOString();

mkdirSync(OUT, { recursive: true });
if (SHOTS) mkdirSync(SHOTS, { recursive: true });

// ---------------------------------------------------------------- static server
const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript",
  ".mjs": "text/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".map": "application/json",
};
const serverLog = { requests: [] };
let staticServer = null;
function startStatic() {
  return new Promise((resolve) => {
    staticServer = http.createServer((req, res) => {
      serverLog.requests.push({ method: req.method, url: req.url });
      if (req.method !== "GET" && req.method !== "HEAD") {
        res.writeHead(405); res.end("method not allowed"); return;
      }
      const urlPath = decodeURIComponent((req.url || "/").split("?")[0]);
      let filePath = join(SERVE_DIR, urlPath);
      if (!filePath.startsWith(SERVE_DIR)) { res.writeHead(403); res.end(); return; }
      if (!existsSync(filePath) || statSync(filePath).isDirectory()) {
        filePath = join(SERVE_DIR, "index.html");
      }
      try {
        const body = readFileSync(filePath);
        res.writeHead(200, { "content-type": MIME[extname(filePath)] || "application/octet-stream" });
        res.end(body);
      } catch {
        res.writeHead(404); res.end("nf");
      }
    });
    staticServer.listen(PORT, "127.0.0.1", () => resolve(PORT));
  });
}
function stopStatic() { return new Promise((r) => (staticServer ? staticServer.close(() => r()) : r())); }

// ---------------------------------------------------------------- scratch fixtures (controls)
const scratchLog = { requests: [] };
const FIXTURES = {
  "/fit.html": `<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1"></head><body style="margin:0"><div id="box" style="width:100%;height:40px;background:#ddd">fit</div></body></html>`,
  "/overflow.html": `<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1"></head><body style="margin:0"><div id="box" style="width:100%;height:40px;background:#ddd">fit</div><div id="wide" style="width:1200px;height:8px;background:#000"></div></body></html>`,
  "/spacing-pass.html": `<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1"><style>body{margin:0;font-family:sans-serif}</style></head><body>
<button id="p1" style="width:20px;height:20px;padding:0;margin:0 4px 0 0">a</button><button id="p2" style="width:20px;height:20px;padding:0">b</button>
</body></html>`,
  "/spacing-fail.html": `<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1"><style>body{margin:0;font-family:sans-serif}</style></head><body>
<button id="f1" style="width:20px;height:20px;padding:0;margin:0">a</button><button id="f2" style="width:20px;height:20px;padding:0">b</button>
</body></html>`,
  "/contrast.html": `<!doctype html><html><head><meta charset=utf-8><style>body{margin:0;background:#ffffff;font-family:sans-serif}
#c1{color:#767676;background:#ffffff}#c2{color:#777777;background:#ffffff}#c3{color:#000000;background:#ffffff}#c4{color:#ffffff;background:#ffffff}</style></head><body>
<span id="c1">one</span><span id="c2">two</span><span id="c3">three</span><span id="c4">four</span>
</body></html>`,
  "/guard.html": `<!doctype html><html><head><meta charset=utf-8></head><body><div id="r">pending</div>
<script>window.__postResult="pending";
fetch("/probe",{method:"POST",body:"synthetic"})
  .then(function(r){window.__postResult="resolved:"+r.status;document.getElementById("r").textContent=window.__postResult})
  .catch(function(e){window.__postResult="rejected:"+e.name;document.getElementById("r").textContent=window.__postResult});
</script></body></html>`,
};
let scratchServer = null;
let scratchPort = 0;
function startScratch() {
  return new Promise((resolve) => {
    scratchServer = http.createServer((req, res) => {
      scratchLog.requests.push({ method: req.method, url: req.url });
      if (req.method !== "GET" && req.method !== "HEAD") {
        res.writeHead(405); res.end("method not allowed"); return;
      }
      const body = FIXTURES[req.url];
      if (!body) { res.writeHead(404); res.end("nf"); return; }
      res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
      res.end(body);
    });
    scratchServer.listen(0, "127.0.0.1", () => { scratchPort = scratchServer.address().port; resolve(scratchPort); });
  });
}
function stopScratch() { return new Promise((r) => (scratchServer ? scratchServer.close(() => r()) : r())); }

// ---------------------------------------------------------------- CDP client
class CDP {
  constructor(wsUrl) { this.ws = new WebSocket(wsUrl); this.id = 0; this.pending = new Map(); this.events = []; this.listeners = []; }
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
  const userDir = `/tmp/opencode/sg190/profile-${Date.now()}`;
  const browserHome = "/tmp/opencode/sg190/home";
  mkdirSync(browserHome, { recursive: true });
  const args = [
    `--headless`,
    `--no-sandbox`,
    `--remote-debugging-port=0`,
    `--user-data-dir=${userDir}`,
    `--no-first-run`, `--no-default-browser-check`,
    `--disable-gpu`,
    `--disable-dev-shm-usage`,
    `--force-device-scale-factor=1`,
    `--window-size=1280,900`,
    "about:blank",
  ];
  const child = spawn(BROWSER, args, { stdio: ["ignore", "ignore", "pipe"], env: { ...process.env, HOME: browserHome, XDG_CONFIG_HOME: browserHome + "/.config" } });
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
  var path = function(el){ var p=[]; var n=el; while(n && n.nodeType===1 && p.length<6){ var s=n.tagName.toLowerCase(); if(n.className && typeof n.className==='string'){ var c=n.className.trim().split(/\\s+/).slice(0,3).join('.'); if(c) s+='.'+c; } p.unshift(s); n=n.parentElement; } return p.join('>'); };
  var out = {
    requested: opts.wv, devicePixelRatio: window.devicePixelRatio,
    ua: navigator.userAgent,
    innerWidth_window: window.innerWidth, innerHeight_window: window.innerHeight,
    docEl_clientWidth: document.documentElement.clientWidth, docEl_clientHeight: document.documentElement.clientHeight,
    docEl_scrollWidth: document.documentElement.scrollWidth, docEl_scrollHeight: document.documentElement.scrollHeight,
    body_scrollWidth: document.body.scrollWidth,
    docEl_rect: rect(document.documentElement),
    visualViewport: window.visualViewport ? {width:R(window.visualViewport.width),height:R(window.visualViewport.height),scale:window.visualViewport.scale,offsetLeft:R(window.visualViewport.offsetLeft),offsetTop:R(window.visualViewport.offsetTop)} : null,
    docOverflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    docOverflowY: document.documentElement.scrollHeight - document.documentElement.clientHeight,
  };
  var maxX = document.documentElement.scrollWidth - document.documentElement.clientWidth;
  window.scrollTo(maxX, 0);
  out.horizontalScrollability = { maxScrollX: maxX, reachedScrollX: R(window.scrollX) };
  window.scrollTo(0, 0);
  var sticky = null;
  var allDivs = document.querySelectorAll('div');
  for (var sdi=0; sdi<allDivs.length; sdi++){ if (getComputedStyle(allDivs[sdi]).position === 'sticky') { sticky = allDivs[sdi]; break; } }
  out.stickyShell = sticky ? { path: path(sticky), rect: rect(sticky), height: R(sticky.getBoundingClientRect().height) } : null;
  var nav = document.querySelector('nav');
  if (nav) {
    var cs = getComputedStyle(nav);
    out.nav = { path: path(nav), clientWidth: nav.clientWidth, clientHeight: nav.clientHeight, scrollWidth: nav.scrollWidth, rect: rect(nav), computedOverflowX: cs.overflowX, computedDisplay: cs.display, computedFlexWrap: cs.flexWrap };
    out.navLinks = [];
    var links = nav.querySelectorAll('a');
    for (var j=0;j<links.length;j++){ var lr = links[j].getBoundingClientRect(); out.navLinks.push({ text: (links[j].textContent||'').trim().slice(0,30), rect: rect(links[j]), visible: lr.width>0 && lr.right <= vpW+1 && lr.left >= -1 }); }
  }
  out.offenders = [];
  var all = document.querySelectorAll('body *');
  for (var k=0;k<all.length && out.offenders.length<30;k++){
    var el = all[k];
    if (typeof el.className === 'string' && /sr-only|visually-hidden/.test(el.className)) continue;
    var r = el.getBoundingClientRect();
    if (r.width>0 && r.height>0 && (r.right > vpW + 1 || r.left < -1)) {
      out.offenders.push({ path: path(el), rect: rect(el) });
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
  if (opts.menu) {
    var menu = document.getElementById('sg-nav-menu');
    var toggle = document.querySelector('.nav-menu-toggle');
    if (menu && toggle) {
      var mcs = getComputedStyle(menu);
      var menuLinks = [];
      var mls = menu.querySelectorAll('a');
      for (var mi=0; mi<mls.length; mi++){ var mr = mls[mi].getBoundingClientRect(); menuLinks.push({ text:(mls[mi].textContent||'').trim(), rect: rect(mls[mi]), visibleInViewport: mr.width>0 && mr.left>=-1 && mr.right<=vpW+1 }); }
      out.menu = { toggleDisplay: getComputedStyle(toggle).display, menuDisplay: mcs.display, dataOpen: menu.getAttribute('data-open'), links: menuLinks };
    }
  }
  return out;
})()`;

const FOCUS_STEP_JS = `(function(){
  var R=function(n){return Math.round(n*100)/100;};
  var el=document.activeElement;
  if(!el || el===document.body) return { none:true };
  var r=el.getBoundingClientRect();
  var sticky=null;
  var divs=document.querySelectorAll('div');
  for(var i=0;i<divs.length;i++){ if(getComputedStyle(divs[i]).position==='sticky'){ sticky=divs[i]; break; } }
  var obscured=false, stickyBottom=null, stickyHeight=null, insideSticky=false;
  if (sticky){ var s=sticky.getBoundingClientRect(); stickyBottom=R(s.bottom); stickyHeight=R(s.height); insideSticky = sticky.contains(el); obscured = !insideSticky && r.top < s.bottom && r.bottom > s.top; }
  return {
    tag: el.tagName.toLowerCase(),
    name: (el.getAttribute('aria-label') || el.textContent || '').trim().slice(0,50),
    href: el.getAttribute && el.getAttribute('href'),
    rect: { top:R(r.top), bottom:R(r.bottom), left:R(r.left), right:R(r.right), width:R(r.width), height:R(r.height) },
    obscuredBySticky: obscured, insideSticky: insideSticky, stickyBottom: stickyBottom, stickyHeight: stickyHeight,
    scrollY: R(window.scrollY),
    visibleInViewport: r.width>0 && r.height>0 && r.top < window.innerHeight && r.bottom > 0,
  };
})()`;

const MASK_JS = (privates) => `(function(){
  var P = ${JSON.stringify(privates)};
  var blockRun = function(len){ var out=''; for (var i=0;i<len;i++) out += '\u25A0\u200B'; return out; };
  var n=0;
  var imgs=document.querySelectorAll('img, video, canvas');
  for (var i=0;i<imgs.length;i++){ imgs[i].style.filter='blur(14px)'; n++; }
  var fields=document.querySelectorAll('input, textarea');
  for (var f=0; f<fields.length; f++){
    var fv=fields[f].value; if(!fv) continue; var nf=fv;
    for (var q=0;q<P.length;q++){ var sq=P[q]; if (sq && sq.length>=3 && nf.indexOf(sq)>=0) nf=nf.split(sq).join(blockRun(sq.length)); }
    nf=nf.replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi,function(m){return blockRun(m.length);});
    if (nf!==fv){ fields[f].value=nf; n++; }
  }
  var walker=document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  var t;
  while ((t=walker.nextNode())){
    var v=t.nodeValue; if(!v) continue; var o=v;
    for (var p=0;p<P.length;p++){ var s=P[p]; if (s && s.length>=3 && v.indexOf(s)>=0) v=v.split(s).join(blockRun(s.length)); }
    v=v.replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi,function(m){return blockRun(m.length);});
    if (v!==o) t.nodeValue=v;
  }
  return {blurred:imgs.length, maskedFields:n, privates:P.length, blockRun: "\u25A0 + U+200B (layout-safe line break opportunities)"};
})()`;

// ---------------------------------------------------------------- capture engine
class Session {
  constructor(cdp, versionLabel) { this.cdp = cdp; this.versionLabel = versionLabel; this.guard = { methods: {}, blocked: [], blockedExternal: [] }; this.requestLog = []; }
  async open() {
    const c = await this.cdp.send("Target.createTarget", { url: "about:blank" });
    const a = await this.cdp.send("Target.attachToTarget", { targetId: c.targetId, flatten: true });
    this.sessionId = a.sessionId;
    this.targetId = c.targetId;
    this.cdp.listeners.push((msg) => {
      if (msg.sessionId !== this.sessionId) return;
      if (msg.method === "Fetch.requestPaused") {
        const p = msg.params; const m = p.request.method;
        this.guard.methods[m] = (this.guard.methods[m] || 0) + 1;
        this.requestLog.push({ method: m, url: p.request.url.slice(0, 160) });
        if (m !== "GET" && m !== "HEAD" && m !== "OPTIONS") {
          this.guard.blocked.push({ method: m, url: p.request.url.slice(0, 160) });
          this.cdp.send("Fetch.failRequest", { requestId: p.requestId, errorReason: "AccessDenied" }, this.sessionId).catch(() => {});
          return;
        }
        const u = p.request.url;
        if (u.startsWith(API_ORIGIN + "/")) {
          const lurl = BASE + u.slice(API_ORIGIN.length);
          fetch(lurl, { method: m === "HEAD" ? "GET" : m, redirect: "follow" })
            .then(async (r) => {
              const buf = Buffer.from(await r.arrayBuffer());
              const headers = [];
              for (const [n, v] of r.headers) {
                const ln = n.toLowerCase();
                if (["content-encoding", "content-length", "transfer-encoding"].includes(ln)) continue;
                headers.push({ name: n, value: v });
              }
              headers.push({ name: "Access-Control-Allow-Origin", value: "*" });
              this.fulfilled = (this.fulfilled || 0) + 1;
              return this.cdp.send("Fetch.fulfillRequest", { requestId: p.requestId, responseCode: r.status, responseHeaders: headers, body: buf.toString("base64") }, this.sessionId);
            })
            .catch(() => { this.fulfillFailures = (this.fulfillFailures || 0) + 1; this.cdp.send("Fetch.failRequest", { requestId: p.requestId, errorReason: "ConnectionRefused" }, this.sessionId).catch(() => {}); });
          return;
        }
        if (u.startsWith("http://127.0.0.1:") || u.startsWith("http://localhost:") || u.startsWith("data:") || u.startsWith("blob:")) {
          this.cdp.send("Fetch.continueRequest", { requestId: p.requestId }, this.sessionId).catch(() => {});
          return;
        }
        this.guard.blockedExternal.push({ method: m, url: u.slice(0, 160) });
        this.cdp.send("Fetch.failRequest", { requestId: p.requestId, errorReason: "AccessDenied" }, this.sessionId).catch(() => {});
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
  async pressTab(times) {
    for (let i = 0; i < times; i++) {
      await this.cdp.send("Input.dispatchKeyEvent", { type: "rawKeyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9, nativeVirtualKeyCode: 9 }, this.sessionId);
      await this.cdp.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9, nativeVirtualKeyCode: 9 }, this.sessionId);
      await sleep(140);
    }
  }
  async measure(opts) { return await this.evaluate(MEASURE_JS(opts)); }
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
      if (cand && cand.id) { reviewPath = `/review/${cand.id}?household_id=${encodeURIComponent(hid)}`; if (cand.fields && cand.fields.display_name) privates.push(String(cand.fields.display_name)); break; }
    }
  }
  return { privates, count: privates.length, assetId, reviewPath, householdId: hid };
}

// ---------------------------------------------------------------- controls
function assertControl(list, name, ok, detail) {
  list.push({ name, ok: !!ok, detail });
  if (!ok) log("CONTROL FAIL:", name, JSON.stringify(detail));
  return !!ok;
}
function evalTargets(ts) {
  const R = (n) => Math.round(n * 100) / 100;
  const res = [];
  for (let i = 0; i < ts.length; i++) {
    const t = ts[i], r = t.rect;
    const undersized = r.width < 24 || r.height < 24;
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const intersections = [];
    for (let j = 0; j < ts.length; j++) {
      if (i === j) continue;
      const o = ts[j].rect;
      const dx = Math.max(o.left - cx, 0, cx - o.right);
      const dy = Math.max(o.top - cy, 0, cy - o.bottom);
      const edgeDist = Math.hypot(dx, dy);
      const cj = { cx: o.left + o.width / 2, cy: o.top + o.height / 2 };
      const centerDist = Math.hypot(cx - cj.cx, cy - cj.cy);
      const otherUndersized = o.width < 24 || o.height < 24;
      if (edgeDist < 12) intersections.push({ j, rule: "circle-vs-target-rect", edgeDistance: R(edgeDist), other: ts[j].text });
      else if (otherUndersized && centerDist < 24) intersections.push({ j, rule: "circle-vs-circle", centerDistance: R(centerDist), other: ts[j].text });
    }
    const inlineInText = t.computedDisplay === "inline" && !/flex|grid/.test(t.parentDisplay || "") && (t.tag === "a" || t.tag === "span");
    res.push({ text: t.text, tag: t.tag, size: { w: R(r.width), h: R(r.height) }, undersized, circleIntersections: intersections, inlineEvidence: inlineInText ? { display: t.computedDisplay, parentDisplay: t.parentDisplay } : null, disposition: !undersized ? "PASS-SIZE" : (intersections.length === 0 ? "PASS-SPACING" : (inlineInText ? "EXCEPTION-INLINE(candidate)" : "FAIL")) });
  }
  return res;
}

async function runControls(cdp, versionLabel) {
  const results = { controls: [], contrastKnown: [], scratchServerLog: null, guard: null, browser: versionLabel, ts: TS };
  const s = new Session(cdp, versionLabel);
  await s.open();

  await s.setViewport(390, 844);
  await s.navigate(`http://127.0.0.1:${scratchPort}/fit.html`);
  let m = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: false, contrast: false });
  assertControl(results.controls, "scratch_fit_390", m.docOverflowX === 0, { docOverflowX: m.docOverflowX, clientWidth: m.docEl_clientWidth, scrollWidth: m.docEl_scrollWidth });

  await s.navigate(`http://127.0.0.1:${scratchPort}/overflow.html`);
  const landed = await s.evaluate(`(function(){ var w=document.getElementById('wide'); var r=w.getBoundingClientRect(); return { width: Math.round(r.width) }; })()`);
  const mOv = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: false, contrast: false });
  const mutationLanded = landed.width === 1200 && mOv.docOverflowX > 0;
  assertControl(results.controls, "scratch_overflow_390", mutationLanded, { wideRectWidth: landed.width, docOverflowX: mOv.docOverflowX });

  scratchLog.requests.length = 0;
  await s.navigate(`http://127.0.0.1:${scratchPort}/guard.html`);
  await sleep(1200);
  const postResult = await s.evaluate(`window.__postResult`);
  const serverSawPost = scratchLog.requests.some((r) => r.method === "POST");
  const guardBlocked = s.guard.blocked.some((b) => b.method === "POST");
  results.guard = { postResult, serverSawPost, blockedByDriver: guardBlocked, blockedList: s.guard.blocked.slice(), methodsSeen: { ...s.guard.methods } };
  assertControl(results.controls, "transport_guard_post", postResult.startsWith("rejected") && !serverSawPost && guardBlocked, { postResult, serverSawPost, guardBlocked });

  await s.navigate(`http://127.0.0.1:${scratchPort}/spacing-pass.html`);
  let mp = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: true, contrast: false });
  await s.navigate(`http://127.0.0.1:${scratchPort}/spacing-fail.html`);
  let mf = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: true, contrast: false });
  const spacingPassEval = evalTargets(mp.targets);
  const spacingFailEval = evalTargets(mf.targets);
  assertControl(results.controls, "spacing_pass_fixture", spacingPassEval.length === 2 && spacingPassEval.every((x) => x.disposition === "PASS-SPACING"), { got: spacingPassEval.map((x) => x.disposition) });
  assertControl(results.controls, "spacing_fail_fixture", spacingFailEval.length >= 2 && spacingFailEval.slice(0, 2).every((x) => x.disposition === "FAIL"), { got: spacingFailEval.map((x) => x.disposition) });
  results.spacingFixturePass = spacingPassEval;
  results.spacingFixtureFail = spacingFailEval;

  await s.navigate(`http://127.0.0.1:${scratchPort}/contrast.html`);
  const mc = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: false, contrast: true, contrastCap: 10 });
  const get = (txt) => { const c = mc.contrast.find((x) => x.text === txt); return c ? c.ratio_exact : undefined; };
  const known = [
    ["#767676 on #ffffff", get("one"), 4.54, 0.01],
    ["#777777 on #ffffff", get("two"), 4.48, 0.01],
    ["#000000 on #ffffff", get("three"), 21, 0.01],
    ["#ffffff on #ffffff", get("four"), 1, 0.001],
  ];
  for (const [n, v, exp, tol] of known) results.contrastKnown.push({ case: n, computed: v, expected: exp, ok: v !== undefined && Math.abs(v - exp) <= tol });
  const wrongExpectation = { case: "#767676 on #ffffff == 5.0 (deliberately wrong control)", computed: get("one"), expected: 5.0 };
  wrongExpectation.ok = wrongExpectation.computed !== undefined && Math.abs(wrongExpectation.computed - 5.0) <= 0.01;
  results.contrastKnown.push(wrongExpectation);
  assertControl(results.controls, "contrast_known_controls", results.contrastKnown.slice(0, 4).every((k) => k.ok), { cases: results.contrastKnown.slice(0, 4) });
  assertControl(results.controls, "contrast_wrong_expectation_must_fail", wrongExpectation.ok === false, wrongExpectation);

  results.scratchServerLog = { requests: scratchLog.requests.slice(0, 20) };
  await s.close();
  return results;
}

// ---------------------------------------------------------------- app run
async function runApp(cdp, versionLabel) {
  const priv = await resolvePrivates();
  log("resolved: asset?", !!priv.assetId, "review?", !!priv.reviewPath, "private values:", priv.count);
  const routes = [
    { name: "catalog", path: "/", targets: true, contrast: true },
    { name: "capture", path: "/capture", targets: true },
    { name: "asset_detail", path: priv.assetId ? `/assets/${priv.assetId}?household_id=${priv.householdId}` : null, targets: true, contrast: true },
    { name: "settings", path: "/settings", targets: true },
    { name: "inbox", path: "/inbox", targets: true, contrast: true },
    { name: "planning", path: "/planning", targets: true },
    { name: "chat", path: "/chat", targets: true },
    { name: "analytics", path: "/analytics", targets: true },
    { name: "expiry", path: "/expiry", targets: true, contrast: true },
    { name: "review", path: priv.reviewPath, targets: true, contrast: true },
  ];
  const viewports = [[390, 844], [834, 1112], [1440, 900], [320, 720]];
  const app = { viewports, routes: [], screenshots: [], tabProbes: [], menuProbes: [], draftProbe: null, guardAggregate: null, evaluator: "evalTargets (shared with fixture controls)" };
  const s = new Session(cdp, versionLabel);
  await s.open();
  const scrub = (o) => {
    if (typeof o === "string") { let v = o; for (const p of priv.privates) if (p && p.length >= 3 && v.includes(p)) v = v.split(p).join("■".repeat(p.length)); v = v.replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, (m) => "■".repeat(2)); return v; }
    if (Array.isArray(o)) return o.map(scrub);
    if (o && typeof o === "object") { for (const k of Object.keys(o)) o[k] = scrub(o[k]); return o; }
    return o;
  };
  for (const rt of routes) {
    for (const [w, h] of viewports) {
      const publicPath = rt.name === "asset_detail" ? "/assets/{asset_id}" : rt.name === "review" ? "/review/{candidate_id}" : rt.path;
      const rec = { route: rt.name, path: publicPath, viewport: `${w}x${h}` };
      if (!rt.path) { rec.error = "route path unresolvable (no candidate/asset id from loopback GET)"; rec.measured = false; app.routes.push(rec); continue; }
      try {
        await s.setViewport(w, h);
        await s.navigate("http://127.0.0.1:" + PORT + rt.path);
        const m = await s.measure({ wv: { width: w, height: h, dpr: 1 }, targets: !!rt.targets, contrast: !!rt.contrast, contrastCap: 80, menu: true });
        rec.measured = true;
        rec.measure = scrub(JSON.parse(JSON.stringify(m)));
        if (rt.targets && m.targets) rec.targetDispositions = scrub(evalTargets(JSON.parse(JSON.stringify(m.targets))));
        if (m.menu) {
          const menuProbe = { route: rt.name, viewport: `${w}x${h}`, ...scrub(JSON.parse(JSON.stringify(m.menu))) };
          if (w === 390) app.menuProbes.push({ phase: "closed", ...menuProbe });
        }
        if (SHOTS) {
          const maskInfo = await s.mask(priv.privates);
          rec.mask = { ...maskInfo, order: "after_measurement_before_screenshot" };
          const postMask = await s.evaluate(`(function(){ return { docOverflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth, docEl_clientWidth: document.documentElement.clientWidth, docEl_scrollWidth: document.documentElement.scrollWidth }; })()`);
          rec.postMaskGeometry = postMask;
          const file = `${SHOTS}/${rt.name}_${w}x${h}.jpg`;
          await s.screenshot(file);
          rec.screenshot = file;
          app.screenshots.push({ file, route: rt.name, viewport: `${w}x${h}`, stage: "measured first, privacy-masked before capture", redaction: "img/video/canvas blur14px; household/asset display names and UUID-shaped runs replaced" });
        }
      } catch (e) {
        rec.error = String(e).slice(0, 400);
      }
      app.routes.push(rec);
      log("app", rt.name, `${w}x${h}`, rec.error ? "ERROR " + rec.error.slice(0, 120) : "ok");
    }
  }

  // narrow-menu interaction probe at 390 on analytics
  try {
    await s.setViewport(390, 844);
    await s.navigate("http://127.0.0.1:" + PORT + "/analytics");
    await s.evaluate(`(function(){ var t=document.querySelector('.nav-menu-toggle'); t.click(); return getComputedStyle(document.getElementById('sg-nav-menu')).display; })()`);
    await sleep(200);
    const open = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: false, contrast: false, menu: true });
    app.menuProbes.push({ phase: "open-clicked", route: "analytics", viewport: "390x844", ...scrub(open.menu) });
    if (SHOTS) {
      await s.mask(priv.privates);
      const file = `${SHOTS}/menu_open_390x844.jpg`;
      await s.screenshot(file);
      app.screenshots.push({ file, route: "analytics-menu-open", viewport: "390x844", stage: "measured first, privacy-masked before capture", redaction: "same as route captures" });
    }
    app.menuProbes.push({ phase: "toggle-hidden-1440", route: "analytics", viewport: "1440x900", ...(await (async () => {
      await s.setViewport(1440, 900);
      const m = await s.measure({ wv: { width: 1440, height: 900, dpr: 1 }, targets: false, contrast: false, menu: true });
      return scrub(m.menu);
    })()) });
  } catch (e) {
    app.menuProbes.push({ error: String(e).slice(0, 300) });
  }

  // normal-Tab probe on the catalog (sticky shell): 30 Tabs, none obscured
  try {
    await s.setViewport(390, 844);
    await s.navigate("http://127.0.0.1:" + PORT + "/");
    await s.evaluate(`document.body.focus ? document.body.focus() : null`);
    const steps = [];
    let obscuredCount = 0, invisibleCount = 0;
    for (let i = 0; i < 30; i++) {
      await s.pressTab(1);
      const step = await s.evaluate(FOCUS_STEP_JS);
      steps.push({ i: i + 1, ...scrub(step) });
      if (step.obscuredBySticky) obscuredCount++;
      if (!step.none && !step.visibleInViewport) invisibleCount++;
    }
    app.tabProbes.push({ route: "catalog", viewport: "390x844", tabs: 30, obscuredCount, invisibleCount, steps: steps.filter((x) => !x.none) });
    if (SHOTS) {
      await s.mask(priv.privates);
      const file = `${SHOTS}/tab_focus_catalog_390x844.jpg`;
      await s.screenshot(file);
      app.screenshots.push({ file, route: "catalog-tab-focus", viewport: "390x844", stage: "measured first, privacy-masked before capture", redaction: "same as route captures" });
    }
  } catch (e) {
    app.tabProbes.push({ error: String(e).slice(0, 300) });
  }

  // draft preservation: type into catalog search, change viewport, read back
  try {
    await s.setViewport(390, 844);
    await s.navigate("http://127.0.0.1:" + PORT + "/");
    const typed = await s.evaluate(`(function(){
      var input = document.querySelector('input[aria-label="Search catalog"]');
      if (!input) return { found: false };
      var setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
      setter.call(input, 'sg190 draft');
      input.dispatchEvent(new Event('input', { bubbles: true }));
      return { found: true, valueAfterType: input.value, active: document.activeElement === input };
    })()`);
    await s.setViewport(834, 1112);
    await sleep(300);
    await s.setViewport(390, 844);
    await sleep(300);
    const after = await s.evaluate(`(function(){ var input = document.querySelector('input[aria-label="Search catalog"]'); return input ? input.value : null; })()`);
    app.draftProbe = { typed, valueAfterViewportRoundTrip: after, preserved: typed.found && after === "sg190 draft" };
    if (SHOTS) {
      await s.evaluate(`(function(){ var i=document.querySelector('input[aria-label="Search catalog"]'); if(i){ var s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set; s.call(i,''); i.dispatchEvent(new Event('input',{bubbles:true})); } })()`);
      await s.mask(priv.privates);
      const file = `${SHOTS}/draft_probe_catalog_390x844.jpg`;
      await s.screenshot(file);
      app.screenshots.push({ file, route: "catalog-draft-probe", viewport: "390x844", stage: "probe done, search cleared, privacy-masked before capture", redaction: "same as route captures" });
    }
  } catch (e) {
    app.draftProbe = { error: String(e).slice(0, 300) };
  }

  app.guardAggregate = { methods: { ...s.guard.methods }, blocked: s.guard.blocked.slice(), blockedExternal: s.guard.blockedExternal.slice(), requestCount: s.requestLog.length, fulfilledFromLoopback: s.fulfilled || 0, fulfillFailures: s.fulfillFailures || 0, apiOrigin: API_ORIGIN };
  await s.close();
  return app;
}

// ---------------------------------------------------------------- main
async function main() {
  const started = Date.now();
  const summary = { ts: TS, browser: null, serve: SERVE_DIR ? { dir: SERVE_DIR, port: PORT } : null, controls: null, app: null, errors: [] };
  if (SERVE_DIR) { await startStatic(); log("static server on 127.0.0.1:" + PORT + " for " + SERVE_DIR); }
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
  if (RUN_APP) summary.app = await runApp(cdp, br.versionInfo["Browser"]);

  try { br.child.kill("SIGTERM"); } catch {}
  summary.staticServerLog = serverLog.requests.slice(0, 60);
  summary.elapsedSeconds = Math.round((Date.now() - started) / 1000);
  const outFile = `${OUT}/result.json`;
  writeFileSync(outFile, JSON.stringify(summary, null, 1));
  await stopStatic();
  await stopScratch();
  log("wrote", outFile, "elapsed", summary.elapsedSeconds + "s");
  const controlFailures = summary.controls ? summary.controls.controls.filter((c) => !c.ok).length : 0;
  const appRoutes = summary.app ? summary.app.routes.filter((r) => r.measured).length : 0;
  console.log(JSON.stringify({ outFile, elapsedSeconds: summary.elapsedSeconds, controlFailures, appRoutesMeasured: appRoutes, errors: summary.errors }));
  process.exit(controlFailures > 0 ? 1 : 0);
}

main().catch((e) => { console.error("FATAL", e); process.exit(2); });
