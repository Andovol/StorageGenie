#!/usr/bin/env node
// SG-199 raw-CDP browser measurement driver (dependency-free; Node >= 22 built-in WebSocket).
// Derived from the audited SG-190 driver (docs/worklogs/SG-190_driver.mjs), itself derived
// from the audited SG-183 driver. Changes for SG-199 (read-only measurement slice):
//   (1) touch phase: mobile:true + Emulation.setTouchEmulationEnabled, CDP Input.dispatchTouchEvent
//       tap probes (nav selector, menu toggle, badge), per-route overflow shots at 390x844;
//   (2) zoom phase: 100% (1280x900 DPR1) vs 200% browser-zoom emulation (640x450 CSS @ DPR2,
//       the standard reflow-equivalent emulation; headless has no native zoom-factor switch)
//       plus card/table density numbers at both levels;
//   (3) dark phase: sg-theme=dark seeded pre-load via Page.addScriptToEvaluateOnNewDocument,
//       contrast + nav-surface sampling, plus driver-scoped simulated read failures so the
//       in-tree role="alert" branches render for sampling (local Fetch fulfillment only);
//   (4) fulfillment fidelity (PG-EV-04): every fulfilled response is byte-compared against a
//       second direct loopback GET; any mismatch is recorded and the run exits non-zero (STOP).
// Read-only by construction: every request is intercepted via Fetch.* and any method other than
// GET/HEAD/OPTIONS is failed BEFORE forwarding; actual methods and reject counters are recorded.
// No credentials, no cookies forwarded, no browser profile access (fresh temp user-data-dir).
//
// Modes (run separately per phase; merge combines the result JSONs):
//   --serve <dir> --port <n>   static SPA server (also serves /__sg199__/fixture.html)
//   --controls                 harness self-checks (fixtures; each has a must-fail arm)
//   --touch / --zoom / --dark  the three measurement axes
//   --merge <files...> --controls <controls.json> --out <measure.json>
//
// Machine summary on stdout (CO-93); progress on stderr.

import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync, readFileSync, existsSync, statSync } from "node:fs";
import { extname, join } from "node:path";
import http from "node:http";
import crypto from "node:crypto";

function log(...a) { console.error("[sg199]", ...a); }
function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }
function sha256(buf) { return crypto.createHash("sha256").update(buf).digest("hex"); }

// PG-EV-04 byte-compare classification. A strict double-GET comparator is the
// packet's price; it fired in vivo on /v1/analytics/summary, whose JSON embeds a
// server-side microsecond wall clock (field "generated_at"). Two sequential reads
// of that endpoint can never be byte-equal. A mismatch is classified clock-only
// ONLY when both bodies parse as JSON and EVERY differing leaf is an
// ISO-date-parseable string under an allowlisted clock field name; anything else
// stays "unexplained" and stops the run.
const CLOCK_FIELD_ALLOWLIST = ["generated_at"];
function diffLeafPaths(a, b, prefix = "") {
  if (typeof a !== typeof b) return [{ path: prefix, a, b }];
  if (a === null || b === null || typeof a !== "object") return a === b ? [] : [{ path: prefix, a, b }];
  const out = [];
  if (Array.isArray(a) || Array.isArray(b)) {
    const n = Math.max((a || []).length, (b || []).length);
    for (let i = 0; i < n && out.length <= 10; i++) out.push(...diffLeafPaths(a ? a[i] : undefined, b ? b[i] : undefined, `${prefix}[${i}]`));
    return out;
  }
  const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
  for (const k of keys) {
    if (out.length > 10) break;
    out.push(...diffLeafPaths(a[k], b[k], prefix ? `${prefix}.${k}` : k));
  }
  return out;
}
function classifyByteMismatch(buf1, buf2) {
  let a, b;
  try { a = JSON.parse(buf1.toString("utf8")); b = JSON.parse(buf2.toString("utf8")); }
  catch { return { clockOnly: false, diffPaths: [{ path: "(body is not JSON)" }] }; }
  const diffs = diffLeafPaths(a, b);
  const fields = diffs.map((d) => d.path.split(".").pop());
  const isoString = (v) => typeof v === "string" && !Number.isNaN(Date.parse(v));
  const clockOnly = diffs.length > 0 && diffs.length <= 10 &&
    diffs.every((d) => CLOCK_FIELD_ALLOWLIST.includes(d.path.split(".").pop()) && isoString(d.a) && isoString(d.b));
  return { clockOnly, diffPaths: diffs.map((d) => ({ path: d.path, a: typeof d.a === "string" ? d.a.slice(0, 40) : d.a, b: typeof d.b === "string" ? d.b.slice(0, 40) : d.b })), fields };
}

const argv = process.argv.slice(2);
function arg(name, dflt) {
  const i = argv.indexOf("--" + name);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : dflt;
}
function argAll(name) {
  const i = argv.indexOf("--" + name);
  if (i < 0) return [];
  const out = [];
  for (let j = i + 1; j < argv.length && !argv[j].startsWith("--"); j++) out.push(argv[j]);
  return out;
}
const BASE = arg("base", "http://127.0.0.1:8003");
const API_ORIGIN = arg("api-origin", "http://localhost:8003");
const BROWSER = arg("browser", "/home/andrei/.cache/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-linux64/chrome-headless-shell");
const OUT = arg("out", "/tmp/opencode/sg199/out");
const SHOTS = arg("shots", "");
const CONTROLS_OUT = arg("controls-out", "");
const SERVE_DIR = arg("serve", "");
const PORT = parseInt(arg("port", "8011"), 10);
const RUN_CONTROLS = argv.includes("--controls");
const RUN_TOUCH = argv.includes("--touch");
const RUN_ZOOM = argv.includes("--zoom");
const RUN_DARK = argv.includes("--dark");
const MERGE_FILES = argAll("merge");
const TS = new Date().toISOString();

if (!MERGE_FILES.length) {
  mkdirSync(OUT, { recursive: true });
  if (SHOTS) mkdirSync(SHOTS, { recursive: true });
}

// driver-side loopback GET ledger (fulfillment source + fidelity compares + privates)
const loopback = { gets: 0 };

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
const SG199_FIXTURE = `<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1"><title>sg199 fixture</title></head><body style="margin:0;background:#ffffff"><div id="x" style="height:60px;background:#eee">sg199 fixture</div></body></html>`;
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
      if (urlPath === "/__sg199__/fixture.html") {
        res.writeHead(200, { "content-type": MIME[".html"] }); res.end(SG199_FIXTURE); return;
      }
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
  "/tap.html": `<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width, initial-scale=1"><style>body{margin:0;font-family:sans-serif}</style></head><body>
<button id="t" style="width:120px;height:44px;margin:20px">tap-me</button><button id="u" style="width:120px;height:44px;margin:20px">other</button>
<script>
window.__touchLog={t:{touchstart:0,touchend:0,click:0},u:{touchstart:0,touchend:0,click:0}};
["t","u"].forEach(function(id){
  var el=document.getElementById(id);
  el.addEventListener("touchstart",function(){window.__touchLog[id].touchstart++;});
  el.addEventListener("touchend",function(){window.__touchLog[id].touchend++;});
  el.addEventListener("click",function(){window.__touchLog[id].click++;});
});
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
  const userDir = `/tmp/opencode/sg199/profile-${Date.now()}`;
  const browserHome = "/tmp/opencode/sg199/home";
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
  var parse = function(s){ var m = s && s.match(/rgba?\\(([^)]+)\\)/); if(!m) return null; var p = m[1].split(',').map(function(x){return parseFloat(x);}); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}; };
  var lin = function(c){ c/=255; return c<=0.04045 ? c/12.92 : Math.pow((c+0.055)/1.055,2.4); };
  var lum = function(c){ return 0.2126*lin(c.r)+0.7152*lin(c.g)+0.0722*lin(c.b); };
  var over = function(fg,bg){ var a=fg.a; return {r:fg.r*a+bg.r*(1-a),g:fg.g*a+bg.g*(1-a),b:fg.b*a+bg.b*(1-a),a:1}; };
  var effBg = function(el){
    var chain=[]; var n=el; var imageFound=null; var opacityChain=[]; var allOpaque=true;
    while (n && n.nodeType===1){ var cs=getComputedStyle(n); if (cs.backgroundImage && cs.backgroundImage!=='none') imageFound = path(n); var c=parse(cs.backgroundColor); if (!c || c.a<1) allOpaque=false; chain.push(c); if (parseFloat(cs.opacity)<1) opacityChain.push({path:path(n),opacity:cs.opacity}); n=n.parentElement; }
    var bg = {r:255,g:255,b:255,a:1};
    for (var i=chain.length-1;i>=0;i--){ var c2=chain[i]; if (c2) bg=over(c2,bg); }
    return {bg:bg, imageBackdrop: imageFound, opacityChain: opacityChain, chainDepth: chain.length, chainAllOpaque: allOpaque};
  };
  var ratioOf = function(fg,bg){ var l1=lum(fg), l2=lum(bg); return Math.round(((Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05))*10000)/10000; };
  var out = {
    requested: opts.wv, devicePixelRatio: window.devicePixelRatio,
    ua: navigator.userAgent,
    maxTouchPoints: navigator.maxTouchPoints, ontouchstart: ('ontouchstart' in window),
    innerWidth_window: window.innerWidth, innerHeight_window: window.innerHeight,
    docEl_clientWidth: document.documentElement.clientWidth, docEl_clientHeight: document.documentElement.clientHeight,
    docEl_scrollWidth: document.documentElement.scrollWidth, docEl_scrollHeight: document.documentElement.scrollHeight,
    body_scrollWidth: document.body.scrollWidth,
    docEl_rect: rect(document.documentElement),
    htmlClassDark: document.documentElement.classList.contains('dark'),
    storedTheme: (function(){ try { return window.localStorage.getItem('sg-theme'); } catch(e){ return 'unreadable:'+e.name; } })(),
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
      out.offenders.push({ path: path(el), rect: rect(el), excessRight: R(r.right - vpW) });
    }
  }
  if (opts.targets) {
    var tsel = 'a[href], button, select, input, textarea, [role="button"], [role="link"], [role="tab"]';
    var tEls = document.querySelectorAll(tsel);
    var chip = document.querySelector('[aria-label^="Total loaded items"]');
    var headerEl = chip && chip.parentElement ? chip.parentElement : null;
    out.targets = [];
    for (var t=0;t<tEls.length;t++){
      var e = tEls[t];
      if (e.disabled) continue;
      var rr = e.getBoundingClientRect();
      if (rr.width<=0 || rr.height<=0) continue;
      if (getComputedStyle(e).visibility === 'hidden') continue;
      var ecs = getComputedStyle(e);
      out.targets.push({ tag: e.tagName.toLowerCase(), type: e.getAttribute('type')||'', role: e.getAttribute('role')||'', text: (e.textContent||e.getAttribute('aria-label')||'').trim().slice(0,40), path: path(e), rect: rect(e), actionableArea: R(rr.width*rr.height), computedDisplay: ecs.display, parentDisplay: e.parentElement?getComputedStyle(e.parentElement).display:'', fontSize: ecs.fontSize, fontWeight: ecs.fontWeight, inNavShell: (nav?nav.contains(e):false) || (headerEl?headerEl.contains(e):false) });
    }
  }
  if (opts.contrast) {
    out.contrast = [];
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var tv;
    while ((tv = walker.nextNode()) && out.contrast.length < ${opts.contrastCap || 60}) {
      var txt = (tv.nodeValue||'').trim();
      if (txt.length < 2) continue;
      var el2 = tv.parentElement;
      if (!el2) continue;
      var r2 = el2.getBoundingClientRect();
      if (r2.width<=0 || r2.height<=0) continue;
      var cs2 = getComputedStyle(el2);
      if (cs2.visibility==='hidden' || cs2.display==='none') continue;
      var fg = parse(cs2.color); if (!fg) continue;
      var eb = effBg(el2);
      var effFg = eb.bg ? over(fg, eb.bg) : null;
      var ratio = null;
      if (effFg && !eb.imageBackdrop) { ratio = ratioOf(effFg, eb.bg); }
      var fs = parseFloat(cs2.fontSize); var fw = parseInt(cs2.fontWeight)||400;
      var large = fs>=24 || (fw>=700 && fs>=18.66);
      out.contrast.push({ text: txt.slice(0,40), path: path(el2), fg_computed: cs2.color, fg_rgba: fg, bg_effective: eb.bg, backdrop_image: eb.imageBackdrop, opacity_chain: eb.opacityChain, fontSize: cs2.fontSize, fontWeight: cs2.fontWeight, largeText: large, ratio_exact: ratio, passesAA: ratio===null?null:(large?ratio>=3:ratio>=4.5), unknown: eb.imageBackdrop!==null });
    }
  }
  if (opts.surfaces) {
    out.surfaces = [];
    for (var si=0; si<opts.surfaces.length; si++){
      var spec = opts.surfaces[si];
      var sc = spec.scope ? document.querySelector(spec.scope) : document;
      var se = sc ? sc.querySelector(spec.selector) : null;
      if (!se) { out.surfaces.push({ label: spec.label, selector: spec.selector, present:false }); continue; }
      var sr = se.getBoundingClientRect();
      var scs = getComputedStyle(se);
      var sfg = parse(scs.color);
      var seb = effBg(se);
      var sratio = null;
      if (sfg && seb.bg && !seb.imageBackdrop) sratio = ratioOf(over(sfg, seb.bg), seb.bg);
      var sfs = parseFloat(scs.fontSize); var sfw = parseInt(scs.fontWeight)||400;
      out.surfaces.push({
        label: spec.label, selector: spec.selector, present: true,
        tag: se.tagName.toLowerCase(), text: (se.textContent||se.getAttribute('aria-label')||'').trim().slice(0,40),
        rect: rect(se), visibleInViewport: sr.width>0 && sr.height>0 && sr.left>=-1 && sr.right<=vpW+1 && sr.top<window.innerHeight,
        computedColor: scs.color, fg_rgba: sfg, bg_effective: seb.bg, backdrop_image: seb.imageBackdrop,
        opacity_chain: seb.opacityChain, bgChainAllOpaque: seb.chainAllOpaque, chainDepth: seb.chainDepth,
        fontSize: scs.fontSize, fontWeight: scs.fontWeight, largeText: (sfs>=24 || (sfw>=700 && sfs>=18.66)),
        ratio_exact: sratio,
        sampleMethod: "element computed color vs ancestor background chain (works for select/link text without a laid-out text node)"
      });
    }
  }
  if (opts.density) {
    out.density = { grids: [], tables: [] };
    var els = document.querySelectorAll('body *');
    for (var di=0; di<els.length && out.density.grids.length<20; di++){
      var de = els[di];
      var dcs = getComputedStyle(de);
      if (dcs.display !== 'grid') continue;
      var dr = de.getBoundingClientRect();
      if (dr.width<=0 || dr.height<=0) continue;
      var cols = dcs.gridTemplateColumns;
      var ncols = 0;
      if (cols && cols !== 'none') {
        var depth=0; var cnt=1;
        for (var ci=0; ci<cols.length; ci++){ var ch=cols[ci]; if(ch==='('){depth++;} else if(ch===')'){depth--;} else if(ch===' ' && depth===0){cnt++;} }
        ncols=cnt;
      }
      var visKids=0; var kidRects=[];
      for (var ki=0; ki<de.children.length; ki++){ var kr=de.children[ki].getBoundingClientRect(); if(kr.width>0&&kr.height>0){ visKids++; if(kidRects.length<4) kidRects.push({w:R(kr.width),h:R(kr.height)}); } }
      out.density.grids.push({path:path(de), rect:rect(de), columnsComputed:cols, trackCount:ncols, gap:dcs.rowGap+'/'+dcs.columnGap, children:de.children.length, visibleChildren:visKids, firstChildRects:kidRects});
    }
    var tabs = document.querySelectorAll('table');
    for (var ti=0; ti<tabs.length && out.density.tables.length<10; ti++){
      var te=tabs[ti]; var trr=te.getBoundingClientRect();
      var trs=te.querySelectorAll('tbody tr'); if(trs.length===0) trs=te.querySelectorAll('tr');
      var firstRow=trs.length?trs[0]:null;
      var cellCount= firstRow?firstRow.children.length:0;
      var rowH= firstRow?R(firstRow.getBoundingClientRect().height):null;
      var parent=te.parentElement; var pW=parent?parent.clientWidth:null;
      out.density.tables.push({path:path(te), rect:rect(te), rows:trs.length, firstRowCells:cellCount, firstRowHeight:rowH, tableScrollWidth:te.scrollWidth, parentClientWidth:pW, tableOverflowsParent:(pW!==null && te.scrollWidth>pW+1), fontSize:getComputedStyle(te).fontSize});
    }
  }
  if (opts.menu) {
    var menu = document.getElementById('sg-nav-menu');
    var toggle = document.querySelector('.nav-menu-toggle');
    if (menu && toggle) {
      var mcs = getComputedStyle(menu);
      var menuLinks = [];
      var mls = menu.querySelectorAll('a');
      for (var mi=0; mi<mls.length; mi++){ var mr = mls[mi].getBoundingClientRect(); menuLinks.push({ text:(mls[mi].textContent||'').trim().slice(0,30), rect: rect(mls[mi]), visibleInViewport: mr.width>0 && mr.left>=-1 && mr.right<=vpW+1 }); }
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
  return {
    tag: el.tagName.toLowerCase(),
    name: (el.getAttribute('aria-label') || el.textContent || '').trim().slice(0,50),
    href: el.getAttribute && el.getAttribute('href'),
    rect: { top:R(r.top), bottom:R(r.bottom), left:R(r.left), right:R(r.right), width:R(r.width), height:R(r.height) },
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
const NAV_SURFACE_SPECS = [
  { label: "nav selector (household select)", selector: "select", scope: "nav" },
  { label: "nav badge (inbox open count)", selector: "[data-testid=\"inbox-open-count\"]", scope: "nav" },
  { label: "nav menu toggle", selector: ".nav-menu-toggle", scope: "nav" },
  { label: "nav brand link", selector: "a", scope: "nav" },
  { label: "nav inbox link", selector: "a[href=\"/inbox\"]", scope: "nav" },
  { label: "nav import link", selector: "a[href=\"/capture\"]", scope: "nav" },
  { label: "nav theme toggle", selector: "button[aria-label^=\"Switch to\"]", scope: "nav" },
  { label: "nav alert (role=alert)", selector: "div[role=\"alert\"]", scope: "nav" },
  { label: "page alert (role=alert)", selector: "div[role=\"alert\"]" },
  { label: "header loaded chip", selector: "[aria-label^=\"Total loaded items\"]" },
];

class Session {
  constructor(cdp, versionLabel) { this.cdp = cdp; this.versionLabel = versionLabel; this.guard = { methods: {}, blocked: [], blockedExternal: [] }; this.requestLog = []; this.failPatterns = []; this.byteMismatches = []; this.bytesCompared = 0; }
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
          const rel = u.slice(API_ORIGIN.length);
          if (this.failPatterns.some((pf) => rel.includes(pf))) {
            this.fulfilled = (this.fulfilled || 0) + 1;
            this.simulatedFailures = (this.simulatedFailures || 0) + 1;
            const body = Buffer.from(JSON.stringify({ detail: "SG-199 driver-scoped simulated read failure (fulfillment-scoped probe)" }));
            this.cdp.send("Fetch.fulfillRequest", { requestId: p.requestId, responseCode: 500, responseHeaders: [ { name: "content-type", value: "application/json" }, { name: "Access-Control-Allow-Origin", value: "*" } ], body: body.toString("base64") }, this.sessionId).catch(() => {});
            return;
          }
          const lurl = BASE + rel;
          (async () => {
            try {
              loopback.gets++;
              const r1 = await fetch(lurl, { method: m === "HEAD" ? "GET" : m, redirect: "follow" });
              const buf1 = Buffer.from(await r1.arrayBuffer());
              loopback.gets++;
              const r2 = await fetch(lurl, { method: m === "HEAD" ? "GET" : m, redirect: "follow" });
              const buf2 = Buffer.from(await r2.arrayBuffer());
              const s1 = sha256(buf1), s2 = sha256(buf2);
              this.bytesCompared += buf1.length;
              if (s1 !== s2) {
                const cls = classifyByteMismatch(buf1, buf2);
                if (cls.clockOnly) {
                  this.byteMismatchClock = (this.byteMismatchClock || 0) + 1;
                  this.byteMismatches.push({ url: rel.slice(0, 120), sha_fulfilled: s1, sha_direct: s2, classification: "nondeterministic_clock_field", diffPaths: cls.diffPaths, fields: cls.fields });
                } else {
                  this.byteMismatchUnexplained = (this.byteMismatchUnexplained || 0) + 1;
                  this.byteMismatches.push({ url: rel.slice(0, 120), sha_fulfilled: s1, sha_direct: s2, classification: "unexplained", diffPaths: cls.diffPaths });
                }
              }
              const headers = [];
              for (const [n, v] of r1.headers) {
                const ln = n.toLowerCase();
                if (["content-encoding", "content-length", "transfer-encoding"].includes(ln)) continue;
                headers.push({ name: n, value: v });
              }
              headers.push({ name: "Access-Control-Allow-Origin", value: "*" });
              this.fulfilled = (this.fulfilled || 0) + 1;
              await this.cdp.send("Fetch.fulfillRequest", { requestId: p.requestId, responseCode: r1.status, responseHeaders: headers, body: buf1.toString("base64") }, this.sessionId);
            } catch (e) {
              this.fulfillFailures = (this.fulfillFailures || 0) + 1;
              this.cdp.send("Fetch.failRequest", { requestId: p.requestId, errorReason: "ConnectionRefused" }, this.sessionId).catch(() => {});
            }
          })();
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
  async configure(w, h, dpr, mobile, touch) {
    this.viewport = { width: w, height: h, dpr, mobile, touch: !!touch };
    await this.cdp.send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: dpr, mobile: !!mobile, screenWidth: w, screenHeight: h }, this.sessionId);
    await this.cdp.send("Emulation.setTouchEmulationEnabled", { enabled: !!touch, maxTouchPoints: touch ? 5 : 1 }, this.sessionId).catch(() => {});
  }
  async setViewport(w, h) { return this.configure(w, h, 1, false, false); }
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
  async tapSelector(sel) {
    const pre = await this.evaluate(`(function(){
      var el=document.querySelector(${JSON.stringify(sel)});
      if(!el) return {found:false, reason:'selector-not-found'};
      var r=el.getBoundingClientRect();
      if (r.width<=0 || r.height<=0) return {found:false, reason:'zero-rect (hidden)'};
      var vpW=document.documentElement.clientWidth, vpH=document.documentElement.clientHeight;
      if (r.top < 0 || r.bottom > vpH || r.left < 0 || r.right > vpW) { el.scrollIntoView({block:'center', inline:'center'}); r=el.getBoundingClientRect(); }
      var cx=r.left+r.width/2, cy=r.top+r.height/2;
      var inside = cx>=0 && cx<=vpW && cy>=0 && cy<=vpH;
      var pts=[[r.left+r.width/2, r.top+r.height/2]];
      return {found:true, rect:{left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height}, point:{x:cx,y:cy}, insideViewport:inside, pathBefore: location.pathname, scrollY: window.scrollY};
    })()`);
    if (!pre.found || !pre.insideViewport) return { ok: false, ...pre };
    const { x, y } = pre.point;
    await this.cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y, radiusX: 1, radiusY: 1, force: 1, id: 1 }] }, this.sessionId);
    await sleep(70);
    await this.cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] }, this.sessionId);
    await sleep(400);
    const post = await this.evaluate(`(function(){
      var ae=document.activeElement;
      var r={activeTag: ae?ae.tagName.toLowerCase():null, activeName: ae?(ae.getAttribute('aria-label')||(ae.textContent||'').trim().slice(0,30)):null, pathAfter: location.pathname, hit:null};
      var elAt = document.elementFromPoint(${JSON.stringify(x)}, ${JSON.stringify(y)});
      if (elAt){ var p=[]; var n=elAt; while(n&&n.nodeType===1&&p.length<4){ p.unshift(n.tagName.toLowerCase()); n=n.parentElement; } r.hit=p.join('>'); }
      return r;
    })()`);
    return { ok: true, ...pre, ...post, tapPoint: { x, y }, touchEvents: ["touchStart", "touchEnd"] };
  }
  async pressEscape() {
    await this.cdp.send("Input.dispatchKeyEvent", { type: "rawKeyDown", key: "Escape", code: "Escape", windowsVirtualKeyCode: 27, nativeVirtualKeyCode: 27 }, this.sessionId);
    await this.cdp.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Escape", code: "Escape", windowsVirtualKeyCode: 27, nativeVirtualKeyCode: 27 }, this.sessionId);
    await sleep(120);
  }
  async addDarkSeed() {
    const r = await this.cdp.send("Page.addScriptToEvaluateOnNewDocument", { source: "try{window.localStorage.setItem('sg-theme','dark')}catch(e){}" }, this.sessionId);
    return r.identifier;
  }
  async removeSeedingScript(identifier) {
    if (!identifier) return false;
    return await this.cdp.send("Page.removeScriptToEvaluateOnNewDocument", { identifier }, this.sessionId).then(() => true).catch(() => false);
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
  loopback.gets++;
  const r = await fetch(BASE + path);
  if (!r.ok) return null;
  return await r.json();
}
async function resolvePrivates() {
  const households = (await apiGet("/v1/households")) || [];
  const hid = households[0] && households[0].id;
  const privates = [];
  for (const h of households) if (h.name) privates.push(h.name);
  let assetId = null;
  if (hid) {
    const assets = await apiGet(`/v1/assets?household_id=${encodeURIComponent(hid)}`);
    const items = (assets && assets.items) || [];
    if (items[0]) assetId = items[0].id;
    for (const it of items) if (it.display_name) privates.push(it.display_name);
  }
  return { privates, count: privates.length, assetId, householdId: hid };
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
    res.push({ text: t.text, tag: t.tag, path: t.path, inNavShell: !!t.inNavShell, size: { w: R(r.width), h: R(r.height) }, undersized, circleIntersections: intersections, inlineEvidence: inlineInText ? { display: t.computedDisplay, parentDisplay: t.parentDisplay } : null, disposition: !undersized ? "PASS-SIZE" : (intersections.length === 0 ? "PASS-SPACING" : (inlineInText ? "EXCEPTION-INLINE(candidate)" : "FAIL")) });
  }
  return res;
}
function navShellSummary(evaluated) {
  const nav = evaluated.filter((x) => x.inNavShell);
  const byH = [...nav].sort((a, b) => a.size.h - b.size.h).slice(0, 5);
  const byW = [...nav].sort((a, b) => a.size.w - b.size.w).slice(0, 5);
  const counts = {};
  for (const x of evaluated) counts[x.disposition] = (counts[x.disposition] || 0) + 1;
  return { navShellCount: nav.length, smallestByHeight: byH.map((x) => ({ text: x.text, tag: x.tag, size: x.size, disposition: x.disposition })), smallestByWidth: byW.map((x) => ({ text: x.text, tag: x.tag, size: x.size, disposition: x.disposition })), dispositionCounts: counts };
}
function byteCompareControl() {
  return (async () => {
    loopback.gets++;
    const a1 = Buffer.from(await (await fetch(BASE + "/v1/health")).arrayBuffer());
    loopback.gets++;
    const a2 = Buffer.from(await (await fetch(BASE + "/v1/health")).arrayBuffer());
    loopback.gets++;
    const b = Buffer.from(await (await fetch(BASE + "/v1/households")).arrayBuffer());
    const sameEqual = sha256(a1) === sha256(a2);
    const diffDifferent = sha256(a1) !== sha256(b);
    return { sameEqual, diffDifferent, sha_health_a: sha256(a1), sha_health_b: sha256(a2), sha_households: sha256(b) };
  })();
}

async function runControls(cdp, versionLabel) {
  const results = { controls: [], contrastKnown: [], scratchServerLog: null, guard: null, browser: versionLabel, ts: TS };
  const s = new Session(cdp, versionLabel);
  await s.open();

  await s.configure(390, 844, 1, false, false);
  await s.navigate(`http://127.0.0.1:${scratchPort}/fit.html`);
  let m = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: false, contrast: false });
  assertControl(results.controls, "scratch_fit_390", m.docOverflowX === 0, { docOverflowX: m.docOverflowX, clientWidth: m.docEl_clientWidth, scrollWidth: m.docEl_scrollWidth });

  await s.navigate(`http://127.0.0.1:${scratchPort}/overflow.html`);
  const landed = await s.evaluate(`(function(){ var w=document.getElementById('wide'); var r=w.getBoundingClientRect(); return { width: Math.round(r.width) }; })()`);
  const mOv = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: false, contrast: false });
  const mutationLanded = landed.width === 1200 && mOv.docOverflowX > 0;
  assertControl(results.controls, "scratch_overflow_390", mutationLanded, { wideRectWidth: landed.width, docOverflowX: mOv.docOverflowX });

  // touch emulation axis: negative read (desktop config) then positive read (touch enabled)
  const mtpBefore = await s.evaluate(`navigator.maxTouchPoints`);
  assertControl(results.controls, "touch_emulation_negative", mtpBefore === 0, { maxTouchPoints: mtpBefore, config: "mobile:false touch:false" });
  await s.configure(390, 844, 1, true, true);
  const mtpTouch = await s.evaluate(`({ maxTouchPoints: navigator.maxTouchPoints, ontouchstart: ('ontouchstart' in window), ua: navigator.userAgent })`);
  // observed 2026-10-16: this headless shell exposes maxTouchPoints=5 but NOT the
  // window.ontouchstart property even with emulation on; functional touch delivery is
  // proven by tap_fixture_delivers (touchstart+click counters), not by the property.
  assertControl(results.controls, "touch_emulation_positive", mtpTouch.maxTouchPoints === 5, { ...mtpTouch, config: "mobile:true touch:true maxTouchPoints=5", ontouchstartNote: "property absent in this shell; tap fixture proves delivery" });
  assertControl(results.controls, "touch_emulation_wrong_expectation_must_fail", mtpTouch.maxTouchPoints !== 7, { computed: mtpTouch.maxTouchPoints, wrongExpectation: 7 });

  await s.navigate(`http://127.0.0.1:${scratchPort}/fit.html`);
  const mFitMobile = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: false, contrast: false });
  assertControl(results.controls, "scratch_fit_390_mobile", mFitMobile.docOverflowX === 0 && mFitMobile.docEl_clientWidth === 390, { docOverflowX: mFitMobile.docOverflowX, clientWidth: mFitMobile.docEl_clientWidth, config: "mobile:true touch:true" });
  await s.navigate(`http://127.0.0.1:${scratchPort}/overflow.html`);
  const landedM = await s.evaluate(`(function(){ var w=document.getElementById('wide'); return { width: Math.round(w.getBoundingClientRect().width) }; })()`);
  const mOvMobile = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: false, contrast: false });
  assertControl(results.controls, "scratch_overflow_390_mobile", landedM.width === 1200 && mOvMobile.docOverflowX > 0, { wideRectWidth: landedM.width, docOverflowX: mOvMobile.docOverflowX });

  // tap fixture: a real tap must deliver touchstart+click to the tapped element only
  await s.navigate(`http://127.0.0.1:${scratchPort}/tap.html`);
  const tapProbe = await s.tapSelector("#t");
  const touchLog = await s.evaluate(`window.__touchLog`);
  const tapDelivers = tapProbe.ok === true && touchLog.t.touchstart >= 1 && touchLog.t.click >= 1 && touchLog.u.touchstart === 0 && touchLog.u.click === 0;
  assertControl(results.controls, "tap_fixture_delivers", tapDelivers, { tapProbe: { ok: tapProbe.ok, hit: tapProbe.hit, activeTag: tapProbe.activeTag }, touchLog });
  assertControl(results.controls, "tap_fixture_wrong_expectation_must_fail", touchLog.t.click !== 99, { computed: touchLog.t.click, wrongExpectation: 99 });

  // zoom emulation pair: 100% (1280x900 DPR1) vs 200% (640x450 CSS @ DPR2)
  await s.configure(1280, 900, 1, false, false);
  await s.navigate(`http://127.0.0.1:${scratchPort}/fit.html`);
  const z100 = await s.evaluate(`({ clientWidth: document.documentElement.clientWidth, dpr: window.devicePixelRatio })`);
  await s.configure(640, 450, 2, false, false);
  await s.navigate(`http://127.0.0.1:${scratchPort}/fit.html`);
  const z200 = await s.evaluate(`({ clientWidth: document.documentElement.clientWidth, dpr: window.devicePixelRatio })`);
  assertControl(results.controls, "zoom_emulation_pair", z100.clientWidth === 1280 && z100.dpr === 1 && z200.clientWidth === 640 && z200.dpr === 2, { at100: z100, at200: z200 });
  assertControl(results.controls, "zoom_wrong_expectation_must_fail", z200.clientWidth !== 700, { computedAt200: z200.clientWidth, wrongExpectation: 700 });

  // dark seed axis: checked on the APP ROOT, whose index.html inline script reads
  // sg-theme pre-hydration and toggles html.dark (the packet's stated mechanism)
  await s.configure(390, 844, 1, false, false);
  s.failPatterns = [];
  await s.navigate(`http://127.0.0.1:${PORT}/`);
  const darkNeg = await s.evaluate(`({ stored: window.localStorage.getItem('sg-theme'), htmlDark: document.documentElement.classList.contains('dark'), prefersDark: window.matchMedia('(prefers-color-scheme: dark)').matches })`);
  assertControl(results.controls, "dark_seed_negative", darkNeg.stored === null && darkNeg.htmlDark === false, darkNeg);
  const seedId = await s.addDarkSeed();
  await s.navigate(`http://127.0.0.1:${PORT}/`);
  const darkPos = await s.evaluate(`({ stored: window.localStorage.getItem('sg-theme'), htmlDark: document.documentElement.classList.contains('dark') })`);
  assertControl(results.controls, "dark_seed_positive", darkPos.stored === "dark" && darkPos.htmlDark === true, darkPos);
  assertControl(results.controls, "dark_seed_wrong_expectation_must_fail", darkPos.stored !== "light", { computed: darkPos.stored, wrongExpectation: "light" });
  results.seedRemovedAfterControls = await s.removeSeedingScript(seedId);
  await s.navigate(`http://127.0.0.1:${PORT}/`);
  const darkPost = await s.evaluate(`({ stored: window.localStorage.getItem('sg-theme'), htmlDark: document.documentElement.classList.contains('dark') })`);
  results.seedAfterRemoval = darkPost; // value stays until cleared; profile is per-invocation
  results.seedCleared = await s.evaluate(`(function(){ try { window.localStorage.removeItem('sg-theme'); return window.localStorage.getItem('sg-theme'); } catch(e){ return 'unreadable:'+e.name; } })()`);

  // surfaces probe machinery: a present element yields rect+ratio, an absent one reports present:false
  await s.navigate(`http://127.0.0.1:${PORT}/__sg199__/fixture.html`);
  const mSurf = await s.measure({ wv: { width: 390, height: 844, dpr: 1 }, targets: false, contrast: false, surfaces: [{ label: "fixture present div", selector: "#x" }, { label: "fixture absent div", selector: "#nope" }] });
  const surfOk = mSurf.surfaces && mSurf.surfaces.length === 2 && mSurf.surfaces[0].present === true && mSurf.surfaces[0].ratio_exact > 10 && mSurf.surfaces[1].present === false;
  assertControl(results.controls, "surfaces_probe_present_absent", surfOk, { surfaces: mSurf.surfaces });

  // spacing fixtures (SC 2.5.8 evaluator, shared with app targets)
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

  // contrast known controls + wrong expectation
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

  // transport guard: a real POST must be blocked before forwarding
  scratchLog.requests.length = 0;
  await s.navigate(`http://127.0.0.1:${scratchPort}/guard.html`);
  await sleep(1200);
  const postResult = await s.evaluate(`window.__postResult`);
  const serverSawPost = scratchLog.requests.some((r) => r.method === "POST");
  const guardBlocked = s.guard.blocked.some((b) => b.method === "POST");
  results.guard = { postResult, serverSawPost, blockedByDriver: guardBlocked, blockedList: s.guard.blocked.slice(), methodsSeen: { ...s.guard.methods } };
  assertControl(results.controls, "transport_guard_post", postResult.startsWith("rejected") && !serverSawPost && guardBlocked, { postResult, serverSawPost, guardBlocked });

  // fulfillment fidelity machinery: equal fetches compare equal, different bodies compare different
  const bc = await byteCompareControl();
  assertControl(results.controls, "fulfillment_bytecompare_discriminates", bc.sameEqual === true && bc.diffDifferent === true, bc);
  results.byteCompare = bc;

  // clock-only mismatch classifier: prove the classifier distinguishes clock-only
  // diffs (allowlisted ISO timestamp leaf) from unexplained diffs, and that a
  // non-JSON differing pair is never classified clock-only
  const cl1 = classifyByteMismatch(Buffer.from(JSON.stringify({ a: 1, generated_at: "2026-10-16T00:00:00.000001+00:00" })), Buffer.from(JSON.stringify({ a: 1, generated_at: "2026-10-16T00:00:01.000002+00:00" })));
  const cl2 = classifyByteMismatch(Buffer.from(JSON.stringify({ a: 1, generated_at: "2026-10-16T00:00:00.000001+00:00" })), Buffer.from(JSON.stringify({ a: 2, generated_at: "2026-10-16T00:00:01.000002+00:00" })));
  const cl3 = classifyByteMismatch(Buffer.from("plain-a"), Buffer.from("plain-b"));
  const cl4 = classifyByteMismatch(Buffer.from(JSON.stringify({ generated_at: "not-a-date" })), Buffer.from(JSON.stringify({ generated_at: "still-not-a-date" })));
  assertControl(results.controls, "bytecompare_classifier_clock_vs_unexplained", cl1.clockOnly === true && cl2.clockOnly === false && cl3.clockOnly === false && cl4.clockOnly === false, { clockOnlyPair: cl1, otherFieldDiff: cl2, nonJsonDiff: cl3, nonIsoClock: cl4 });
  results.byteCompareClassifier = { clockOnlyPair: cl1, otherFieldDiff: cl2, nonJsonDiff: cl3, nonIsoClock: cl4 };

  results.scratchServerLog = { requests: scratchLog.requests.slice(0, 20) };
  await s.close();
  return results;
}

// ---------------------------------------------------------------- phase runners
const ROUTE_SET = [
  { name: "catalog", path: "/" },
  { name: "capture", path: "/capture" },
  { name: "inbox", path: "/inbox" },
  { name: "planning", path: "/planning" },
  { name: "analytics", path: "/analytics" },
  { name: "asset_detail", path: null },
];

function makeScrubber(priv) {
  function sc(o) {
    if (typeof o === "string") { let v = o; for (const p of priv.privates) if (p && p.length >= 3 && v.includes(p)) v = v.split(p).join("■".repeat(p.length)); v = v.replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, (m) => "■".repeat(2)); return v; }
    if (Array.isArray(o)) return o.map(sc);
    if (o && typeof o === "object") { for (const k of Object.keys(o)) o[k] = sc(o[k]); return o; }
    return o;
  }
  return sc;
}

async function routePaths(priv) {
  return ROUTE_SET.map((rt) => ({
    ...rt,
    resolved: rt.name === "asset_detail" ? (priv.assetId ? `/assets/${priv.assetId}?household_id=${encodeURIComponent(priv.householdId)}` : null) : rt.path,
    publicPath: rt.name === "asset_detail" ? "/assets/{asset_id}" : rt.path,
  }));
}

async function captureRoute(s, rt, priv, shotName, opts, extraMeasure = {}) {
  const rec = { route: rt.name, path: rt.publicPath };
  if (!rt.resolved) { rec.error = "route path unresolvable (no asset id from loopback GET)"; rec.measured = false; return rec; }
  await s.navigate("http://127.0.0.1:" + PORT + rt.resolved);
  const m = await s.measure({ wv: s.viewport, ...opts, ...extraMeasure });
  rec.measured = true;
  rec.viewportConfig = { ...s.viewport };
  rec.measure = priv.scrub(JSON.parse(JSON.stringify(m)));
  if (opts.targets && m.targets) {
    rec.targetDispositions = priv.scrub(evalTargets(JSON.parse(JSON.stringify(m.targets))));
    rec.navShell = priv.scrub(navShellSummary(evalTargets(JSON.parse(JSON.stringify(m.targets)))));
  }
  if (SHOTS && shotName) {
    const maskInfo = await s.mask(priv.privates);
    rec.mask = { ...maskInfo, order: "after_measurement_before_screenshot" };
    rec.postMaskGeometry = await s.evaluate(`(function(){ return { docOverflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth, docEl_clientWidth: document.documentElement.clientWidth, docEl_scrollWidth: document.documentElement.scrollWidth }; })()`);
    await s.screenshot(`${SHOTS}/${shotName}.jpg`);
    rec.screenshot = `${shotName}.jpg`;
  }
  return rec;
}

async function runTouch(cdp, versionLabel) {
  const priv = { ...(await resolvePrivates()) };
  const scrub = makeScrubber(priv);
  priv.scrub = scrub;
  const routes = await routePaths(priv);
  const t = { axis: "touch", viewportConfig: "390x844 mobile:true touch:true DPR1", routes: [], tapProbes: [], menuBadgeProbe: null, alertProbe: null, screenshots: [], guardAggregate: null };
  const s = new Session(cdp, versionLabel);
  await s.open();
  await s.configure(390, 844, 1, true, true);
  for (const rt of routes) {
    let rec;
    try {
      rec = await captureRoute(s, rt, priv, `touch_${rt.name}_390x844`, { targets: true, contrast: true, contrastCap: 60, menu: true, density: true, surfaces: NAV_SURFACE_SPECS });
      // selector tap probe after the screenshot (touch only, no mouse events anywhere)
      if (rec.measured) {
        const tap = await s.tapSelector("nav select");
        const focusOk = tap.ok === true && tap.activeTag === "select";
        await s.pressEscape();
        rec.selectorTap = { ...scrub(tap), focusOnSelect: focusOk, hoverEventsUsed: 0 };
        t.tapProbes.push({ route: rt.name, target: "nav select", focusOnSelect: focusOk, tap: scrub(JSON.parse(JSON.stringify(tap))) });
      }
    } catch (e) {
      rec = { route: rt.name, path: rt.publicPath, measured: false, error: String(e).slice(0, 400) };
    }
    t.routes.push(rec);
    log("touch", rt.name, rec.error ? "ERROR " + rec.error.slice(0, 120) : "ok");
  }
  // menu toggle + badge functional tap probe on /planning -> tap badge -> /inbox
  try {
    await s.navigate("http://127.0.0.1:" + PORT + "/planning");
    const toggleTap = await s.tapSelector(".nav-menu-toggle");
    await sleep(250);
    const menuState = await s.evaluate(`(function(){ var m=document.getElementById('sg-nav-menu'); return { dataOpen: m?m.getAttribute('data-open'):null, menuDisplay: m?getComputedStyle(m).display:null }; })()`);
    const badgeBox = await s.evaluate(`(function(){
      var R=function(n){return Math.round(n*100)/100;};
      var b=document.querySelector('[data-testid="inbox-open-count"]');
      var link=document.querySelector('#sg-nav-menu a[href="/inbox"]');
      if(!b) return null;
      var r=b.getBoundingClientRect();
      var lr=link?link.getBoundingClientRect():null;
      return { rect:{left:R(r.left),top:R(r.top),right:R(r.right),bottom:R(r.bottom),width:R(r.width),height:R(r.height)}, text:b.textContent, visible:r.width>0&&r.height>0, inboxLinkRect: lr?{left:R(lr.left),top:R(lr.top),right:R(lr.right),bottom:R(lr.bottom),width:R(lr.width),height:R(lr.height)}:null };
    })()`);
    if (SHOTS) {
      await s.mask(priv.privates);
      await s.screenshot(`${SHOTS}/touch_menu_badge_planning_390x844.jpg`);
      t.screenshots.push({ file: "touch_menu_badge_planning_390x844.jpg", route: "planning-menu-open", viewport: "390x844", stage: "menu opened by touch tap, privacy-masked before capture", redaction: "same as route captures" });
    }
    let badgeTap = null;
    if (badgeBox && badgeBox.visible) {
      badgeTap = await s.tapSelector("[data-testid=\"inbox-open-count\"]");
      await sleep(500);
    }
    t.menuBadgeProbe = scrub({
      toggleTap: { ok: toggleTap.ok, hit: toggleTap.hit, activeTag: toggleTap.activeTag },
      menuAfterToggleTap: menuState,
      badge: badgeBox,
      badgeTap: badgeTap ? { ok: badgeTap.ok, pathAfter: badgeTap.pathAfter, hit: badgeTap.hit, touchEvents: badgeTap.touchEvents } : null,
      badgeTapNavigatedToInbox: !!(badgeTap && badgeTap.pathAfter === "/inbox"),
      hoverEventsUsed: 0,
    });
  } catch (e) {
    t.menuBadgeProbe = { error: String(e).slice(0, 300) };
  }
  // alert operability under touch: driver-scoped households read failure on /capture
  try {
    const failuresBefore = s.simulatedFailures || 0;
    s.failPatterns = ["/v1/households"];
    await s.navigate("http://127.0.0.1:" + PORT + "/capture");
    await sleep(1600);
    const m = await s.measure({ wv: s.viewport, targets: false, contrast: true, contrastCap: 60, menu: false, density: false, surfaces: NAV_SURFACE_SPECS });
    const navAlert = (m.surfaces || []).find((x) => x.label === "nav alert (role=alert)");
    const pageAlert = (m.surfaces || []).find((x) => x.label === "page alert (role=alert)");
    const allAlerts = await s.evaluate(`(function(){
      var nav=document.querySelector('nav');
      var els=document.querySelectorAll('div[role="alert"]');
      var out=[];
      for (var i=0;i<els.length;i++){ var e=els[i]; var r=e.getBoundingClientRect(); out.push({ text:(e.textContent||'').trim().slice(0,60), rect:{left:Math.round(r.left*100)/100,top:Math.round(r.top*100)/100,right:Math.round(r.right*100)/100,bottom:Math.round(r.bottom*100)/100,width:Math.round(r.width*100)/100,height:Math.round(r.height*100)/100}, inNav: nav?nav.contains(e):false, visibleInViewport: r.width>0&&r.height>0&&r.left>=-1&&r.right<=document.documentElement.clientWidth+1&&r.top<window.innerHeight }); }
      return out;
    })()`);
    if (SHOTS) {
      await s.mask(priv.privates);
      await s.screenshot(`${SHOTS}/touch_alert_capture_390x844.jpg`);
      t.screenshots.push({ file: "touch_alert_capture_390x844.jpg", route: "capture-alert", viewport: "390x844", stage: "driver-scoped simulated households failure, privacy-masked before capture", redaction: "same as route captures" });
    }
    t.alertProbe = scrub({ simulatedFailure: "/v1/households fulfilled 500 by the driver's local Fetch layer (no service write)", simulatedFailuresServed: (s.simulatedFailures || 0) - failuresBefore, navAlertPresent: !!(navAlert && navAlert.present), navAlert: navAlert || null, pageAlertFirstMatch: pageAlert || null, allRoleAlertElements: allAlerts, alertContrast: (m.contrast || []).filter((x) => /Could not load/.test(x.text)), requiresTap: false, staticText: true });
    s.failPatterns = [];
  } catch (e) {
    t.alertProbe = { error: String(e).slice(0, 300) };
    s.failPatterns = [];
  }
  t.guardAggregate = scrub({ methods: { ...s.guard.methods }, blocked: s.guard.blocked.slice(), blockedExternal: s.guard.blockedExternal.slice(), requestCount: s.requestLog.length, fulfilledFromLoopback: s.fulfilled || 0, fulfillFailures: s.fulfillFailures || 0, simulatedFailures: s.simulatedFailures || 0, byteMismatches: s.byteMismatches.slice(), byteMismatchClock: s.byteMismatchClock || 0, byteMismatchUnexplained: s.byteMismatchUnexplained || 0, bytesCompared: s.bytesCompared, apiOrigin: API_ORIGIN });
  await s.close();
  return t;
}

async function runZoom(cdp, versionLabel) {
  const priv = { ...(await resolvePrivates()) };
  const scrub = makeScrubber(priv);
  priv.scrub = scrub;
  const routes = await routePaths(priv);
  const z = { axis: "zoom", levels: { at100: "1280x900 mobile:false DPR1", at200: "640x450 mobile:false DPR2 (200% browser-zoom emulation: CSS viewport halved, DPR doubled)" }, routes: [], screenshots: [], guardAggregate: null };
  const s = new Session(cdp, versionLabel);
  await s.open();
  for (const rt of routes) {
    const rec = { route: rt.name, path: rt.publicPath, at100: null, at200: null };
    if (!rt.resolved) { rec.error = "route path unresolvable (no asset id from loopback GET)"; z.routes.push(rec); log("zoom", rt.name, "ERROR unresolvable"); continue; }
    for (const [level, w, h, dpr, shot] of [["at100", 1280, 900, 1, `zoom100_${rt.name}_1280x900`], ["at200", 640, 450, 2, `zoom200_${rt.name}_640x450dpr2`]]) {
      let cap = null;
      try {
        await s.configure(w, h, dpr, false, false);
        cap = await captureRoute(s, rt, priv, shot, { targets: false, contrast: false, menu: true, density: true, surfaces: NAV_SURFACE_SPECS });
        if (cap.measure) {
          const offenders = (cap.measure.offenders || []).slice().sort((a, b) => b.excessRight - a.excessRight);
          cap.overflowSummary = { docOverflowX: cap.measure.docOverflowX, offenderCount: cap.measure.offenders ? cap.measure.offenders.length : 0, topOffenders: offenders.slice(0, 5).map((o) => ({ path: o.path, excessRight: o.excessRight })) };
        }
        rec[level] = cap;
      } catch (e) {
        rec[level] = { error: String(e).slice(0, 400) };
      }
      if (cap && cap.screenshot) z.screenshots.push({ file: cap.screenshot, route: rt.name, viewport: `${w}x${h}@${dpr}x`, stage: "measured first, privacy-masked before capture", redaction: "same as SG-190 route captures" });
    }
    z.routes.push(rec);
    log("zoom", rt.name, rec.at100 && rec.at100.measured ? "ok100" : "ERR100", rec.at200 && rec.at200.measured ? "ok200" : "ERR200");
  }
  z.guardAggregate = scrub({ methods: { ...s.guard.methods }, blocked: s.guard.blocked.slice(), blockedExternal: s.guard.blockedExternal.slice(), requestCount: s.requestLog.length, fulfilledFromLoopback: s.fulfilled || 0, fulfillFailures: s.fulfillFailures || 0, simulatedFailures: s.simulatedFailures || 0, byteMismatches: s.byteMismatches.slice(), byteMismatchClock: s.byteMismatchClock || 0, byteMismatchUnexplained: s.byteMismatchUnexplained || 0, bytesCompared: s.bytesCompared, apiOrigin: API_ORIGIN });
  await s.close();
  return z;
}

async function runDark(cdp, versionLabel) {
  const priv = { ...(await resolvePrivates()) };
  const scrub = makeScrubber(priv);
  priv.scrub = scrub;
  const routes = await routePaths(priv);
  const d = { axis: "dark", viewportConfig: "1440x900 mobile:false DPR1; sg-theme=dark seeded pre-load via Page.addScriptToEvaluateOnNewDocument", routes: [], alertProbes: [], darkSeedSelfCheck: null, screenshots: [], guardAggregate: null };
  const s = new Session(cdp, versionLabel);
  await s.open();
  await s.configure(1440, 900, 1, false, false);
  // negative self-check first (no seed, fresh profile), then seed and re-check
  await s.navigate("http://127.0.0.1:" + PORT + "/");
  d.darkSeedNegative = await s.evaluate(`({ stored: window.localStorage.getItem('sg-theme'), htmlDark: document.documentElement.classList.contains('dark'), bodyBg: getComputedStyle(document.body).backgroundColor })`);
  const seedId = await s.addDarkSeed();
  d.darkSeedScriptIdentifier = seedId;
  await s.navigate("http://127.0.0.1:" + PORT + "/");
  d.darkSeedSelfCheck = await s.evaluate(`({ stored: window.localStorage.getItem('sg-theme'), htmlDark: document.documentElement.classList.contains('dark'), bodyBg: getComputedStyle(document.body).backgroundColor })`);
  for (const rt of routes) {
    let rec;
    try {
      rec = await captureRoute(s, rt, priv, `dark_${rt.name}_1440x900`, { targets: false, contrast: true, contrastCap: 80, menu: true, density: true, surfaces: NAV_SURFACE_SPECS });
      if (rec.measure) {
        rec.darkClassOnHtml = rec.measure.htmlClassDark;
        const cs = (rec.measure.contrast || []).filter((x) => x.ratio_exact !== null);
        rec.contrastSummary = { samples: (rec.measure.contrast || []).length, belowAA: cs.filter((x) => x.passesAA === false).length, unknown: (rec.measure.contrast || []).filter((x) => x.unknown).length, minRatio: cs.length ? Math.min(...cs.map((x) => x.ratio_exact)) : null };
      }
    } catch (e) {
      rec = { route: rt.name, path: rt.publicPath, measured: false, error: String(e).slice(0, 400) };
    }
    d.routes.push(rec);
    log("dark", rt.name, rec.error ? "ERROR " + rec.error.slice(0, 120) : "ok dark=" + (rec.darkClassOnHtml === true));
  }
  // alert-branch probes (driver-scoped simulated failures)
  const probes = [
    { name: "capture_households_alert", path: "/capture", fail: ["/v1/households"], shot: "dark_alert_capture_1440x900" },
    { name: "catalog_facets_alert", path: "/", fail: ["/v1/assets/facets", "/v1/saved-searches"], shot: "dark_alert_catalog_1440x900" },
  ];
  for (const probe of probes) {
    try {
      const failuresBefore = s.simulatedFailures || 0;
      s.failPatterns = probe.fail;
      await s.navigate("http://127.0.0.1:" + PORT + probe.path);
      await sleep(1600);
      const m = await s.measure({ wv: s.viewport, targets: false, contrast: true, contrastCap: 80, menu: false, density: false, surfaces: NAV_SURFACE_SPECS });
      const allAlerts = await s.evaluate(`(function(){
        var nav=document.querySelector('nav');
        var els=document.querySelectorAll('div[role="alert"]');
        var out=[];
        for (var i=0;i<els.length;i++){ var e=els[i]; var r=e.getBoundingClientRect(); out.push({ text:(e.textContent||'').trim().slice(0,60), rect:{left:Math.round(r.left*100)/100,top:Math.round(r.top*100)/100,right:Math.round(r.right*100)/100,bottom:Math.round(r.bottom*100)/100,width:Math.round(r.width*100)/100,height:Math.round(r.height*100)/100}, inNav: nav?nav.contains(e):false, visibleInViewport: r.width>0&&r.height>0&&r.left>=-1&&r.right<=document.documentElement.clientWidth+1&&r.top<window.innerHeight }); }
        return out;
      })()`);
      if (SHOTS) {
        await s.mask(priv.privates);
        await s.screenshot(`${SHOTS}/${probe.shot}.jpg`);
        d.screenshots.push({ file: `${probe.shot}.jpg`, route: `${probe.name}`, viewport: "1440x900", stage: "driver-scoped simulated read failure, privacy-masked before capture", redaction: "same as route captures" });
      }
      const alerts = (m.surfaces || []).filter((x) => x.label.includes("role=alert"));
      d.alertProbes.push(scrub({ name: probe.name, simulatedFailures: probe.fail, simulatedFailuresServed: (s.simulatedFailures || 0) - failuresBefore, htmlDark: m.htmlClassDark, alerts, allRoleAlertElements: allAlerts, alertContrast: (m.contrast || []).filter((x) => /Could not load/.test(x.text)), screenshot: `${probe.shot}.jpg` }));
      s.failPatterns = [];
    } catch (e) {
      d.alertProbes.push({ name: probe.name, error: String(e).slice(0, 300) });
      s.failPatterns = [];
    }
  }
  d.guardAggregate = scrub({ methods: { ...s.guard.methods }, blocked: s.guard.blocked.slice(), blockedExternal: s.guard.blockedExternal.slice(), requestCount: s.requestLog.length, fulfilledFromLoopback: s.fulfilled || 0, fulfillFailures: s.fulfillFailures || 0, simulatedFailures: s.simulatedFailures || 0, byteMismatches: s.byteMismatches.slice(), byteMismatchClock: s.byteMismatchClock || 0, byteMismatchUnexplained: s.byteMismatchUnexplained || 0, bytesCompared: s.bytesCompared, apiOrigin: API_ORIGIN });
  await s.close();
  return d;
}

// ---------------------------------------------------------------- merge
const MEASUREMENT_SOURCES = {
  docOverflowX: "DOM: document.documentElement.scrollWidth - document.documentElement.clientWidth at the emulated viewport (SG-183 denominator shape)",
  docOverflowY: "DOM: scrollHeight - clientHeight of documentElement",
  offenders: "DOM: getBoundingClientRect of every body element; right > clientWidth+1 or left < -1; excessRight = right - clientWidth",
  targets: "DOM: querySelectorAll('a[href], button, select, input, textarea, [role=button|link|tab]'), rect + computed display/font; inNavShell = inside <nav> or the AppHeader root div",
  targetDispositions: "shared evalTargets (WCAG 2.5.8 shape of SG-183/190: undersized <24; circle-vs-rect edge<12; circle-vs-circle center<24; inline-in-text exception candidate)",
  contrast: "DOM tree-walker text nodes: computed color over ancestor background chain (alpha composited; image backdrops flagged unknown), WCAG relative-luminance ratio",
  surfaces: "DOM element-level samples (same color/bg chain math) for select/link/badge/alert surfaces that render text without a laid-out text node (closed <select>)",
  density: "DOM computed styles: display:grid elements (computed gridTemplateColumns track count, gaps, visible children, child rects) and <table> elements (row count, first-row cells/height, scrollWidth vs parent clientWidth)",
  tap: "CDP Input.dispatchTouchEvent touchStart+touchEnd at the element center; element hit via document.elementFromPoint; focus via document.activeElement; navigation via location.pathname before/after",
  menuState: "DOM: #sg-nav-menu data-open attribute, computed display; .nav-menu-toggle computed display",
  darkMechanism: "localStorage sg-theme seeded pre-load via Page.addScriptToEvaluateOnNewDocument (runs before any document script; index.html inline script and ThemeProvider.tsx both read it); html.dark class verified in-page",
  touchEmulation: "Emulation.setDeviceMetricsOverride mobile:true + Emulation.setTouchEmulationEnabled(maxTouchPoints=5); verified via navigator.maxTouchPoints and 'ontouchstart' in window",
  zoomEmulation: "200% browser zoom emulated as CSS viewport halved at DPR 2 (1280x900 -> 640x450@2x); headless has no native zoom-factor switch; standard reflow-equivalent emulation",
  fulfillment: "every browser request to the API origin is fulfilled by the driver from the direct loopback GET (127.0.0.1:8003), no credential/cookie forwarding, ACAO injected by the driver; PG-EV-04: every fulfilled response byte-compared (sha256) against a second direct loopback GET before serving; a mismatch is classified: clock-only ONLY when both bodies parse as JSON and every differing leaf is an ISO-date-parseable string under the allowlisted field name generated_at (proven in vivo on /v1/analytics/summary, which embeds a microsecond server clock; classifier contrast fixtures committed); any unexplained mismatch = run exits non-zero (STOP)",
  simulatedFailures: "driver-scoped Fetch fulfillment of 500 for named paths only, to render in-tree role=alert branches; no request reaches the service and no service state changes",
  masking: "post-measurement only: img/video/canvas blur(14px); household/asset display names and UUID-shaped runs replaced with U+25A0+U+200B (layout-safe) in text nodes and form values",
};

async function merge(results, controlsJson, outFile) {
  const merged = { ts: TS, harness: { driver: "docs/worklogs/SG-199_driver.mjs", sha256: sha256(readFileSync(process.argv[1])) }, browser: null, controls: controlsJson, phases: {}, phaseMeta: [], measurementSources: MEASUREMENT_SOURCES, shotsDir: "docs/worklogs/SG-199_shots", loopbackDriverGets: loopback.gets, notes: { baseRef: "automation", resolvePrivates: "loopback GET /v1/households (+ /v1/assets) for the asset-detail route path" } };
  for (const f of results) {
    const r = JSON.parse(readFileSync(f, "utf8"));
    if (!merged.browser && r.browser) merged.browser = r.browser;
    for (const k of ["touch", "zoom", "dark"]) if (r[k]) merged.phases[k] = r[k];
    merged.phaseMeta.push({ file: f, ts: r.ts, elapsedSeconds: r.elapsedSeconds, errorCount: (r.errors || []).length });
  }
  writeFileSync(outFile, JSON.stringify(merged, null, 1));
  return outFile;
}

// ---------------------------------------------------------------- main
async function main() {
  if (MERGE_FILES.length) {
    const outCtrl = CONTROLS_OUT || arg("controls-out", "");
    const controlsJson = outCtrl && existsSync(outCtrl) ? JSON.parse(readFileSync(outCtrl, "utf8")) : null;
    const outFile = await merge(MERGE_FILES, controlsJson, OUT);
    console.log(JSON.stringify({ merged: outFile, phases: MERGE_FILES.length }));
    return;
  }
  const started = Date.now();
  const summary = { ts: TS, browser: null, serve: SERVE_DIR ? { dir: SERVE_DIR, port: PORT } : null, controls: null, touch: null, zoom: null, dark: null, errors: [] };
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
    if (CONTROLS_OUT) writeFileSync(CONTROLS_OUT, JSON.stringify(summary.controls, null, 1));
  }
  if (RUN_TOUCH) summary.touch = await runTouch(cdp, br.versionInfo["Browser"]);
  if (RUN_ZOOM) summary.zoom = await runZoom(cdp, br.versionInfo["Browser"]);
  if (RUN_DARK) summary.dark = await runDark(cdp, br.versionInfo["Browser"]);

  // stop condition: UNEXPLAINED fulfillment byte mismatches (clock-only diffs are
  // classified with exact leaf evidence in byteMismatches; all other diffs stop)
  const unexplained = [summary.touch, summary.zoom, summary.dark].filter(Boolean).reduce((n, p) => n + ((p.guardAggregate && p.guardAggregate.byteMismatchUnexplained) || 0), 0);
  if (unexplained > 0) summary.errors.push(`FULFILLMENT BYTE MISMATCH (unexplained) count=${unexplained} (PG-EV-04 STOP)`);

  try { br.child.kill("SIGTERM"); } catch {}
  summary.staticServerLog = serverLog.requests.slice(0, 60);
  summary.elapsedSeconds = Math.round((Date.now() - started) / 1000);
  writeFileSync(`${OUT}/result.json`, JSON.stringify(summary, null, 1));
  await stopStatic();
  await stopScratch();
  log("wrote", `${OUT}/result.json`, "elapsed", summary.elapsedSeconds + "s");
  const controlFailures = summary.controls ? summary.controls.controls.filter((c) => !c.ok).length : 0;
  const counts = {
    touchRoutes: summary.touch ? summary.touch.routes.filter((r) => r.measured).length : null,
    zoomRoutes: summary.zoom ? summary.zoom.routes.filter((r) => (r.at100 && r.at100.measured) && (r.at200 && r.at200.measured)).length : null,
    darkRoutes: summary.dark ? summary.dark.routes.filter((r) => r.measured).length : null,
  };
  console.log(JSON.stringify({ outFile: `${OUT}/result.json`, elapsedSeconds: summary.elapsedSeconds, controlFailures, ...counts, errors: summary.errors, loopbackDriverGets: loopback.gets }));
  process.exit(controlFailures > 0 ? 1 : (unexplained > 0 ? 3 : 0));
}

main().catch((e) => { console.error("FATAL", e); process.exit(2); });
