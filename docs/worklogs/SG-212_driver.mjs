#!/usr/bin/env node
// SG-212 served-UI smoke driver (dependency-free; Node >= 22 built-in WebSocket).
// Purpose (packet G2/A2): serve the CANDIDATE frontend/dist on 127.0.0.1:5173 — the
// origin the backend's CORS allow-list carries (backend/app/config.py:19) — then drive
// chrome-headless-shell through raw CDP and assert the D-21 content-fit density rule
// ON THE SERVED PAGE:
//   world wide1440 (1440x900, DPR1): the Catalog (/) opens in TABLE (Compact Table
//     aria-pressed), the table container has maxScrollLeft 0, docOverflowX 0; the
//     toggle is then exercised BOTH directions through the real control (CDP mouse
//     press/release at the button centre): -> grid, -> table.
//   world touch390 (390x844, mobile:true, touch:true, maxTouchPoints=5): the Catalog
//     opens in GRID with docOverflowX 0.
// Derived from the audited SG-208 driver (docs/worklogs/SG-208_driver.mjs), itself
// from SG-207; CDP/static-server/mask shapes unchanged. Divergences: two worlds with
// per-world device metrics, a density/toggle probe, three screenshots in the wide
// world + one in touch, and the rule gate (content column width + state + overflow).
// Privacy (CO-44, SG-205/SG-207/SG-208 precedent): masking runs AFTER the initial
// measurement and BEFORE the first screenshot; household_id query VALUES are redacted
// in the committed JSON; asset names never enter the JSON. Read-only: the page
// performs GETs only; no form is submitted. No interactive prompt; every wait is
// bounded; browser exits with the run.
//
// Usage: node SG-212_driver.mjs --world wide1440|touch390 --dist <frontend/dist> --shots <dir> --out <json> [--mask 'sel1|sel2']
// Machine summary on stdout (CO-93); progress on stderr.

import { spawn } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync } from "node:fs";
import { extname, join, dirname } from "node:path";
import http from "node:http";
import crypto from "node:crypto";

function log(...a) { console.error("[sg212]", ...a); }
function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }
function sha256(buf) { return crypto.createHash("sha256").update(buf).digest("hex"); }
const shaFile = (p) => sha256(readFileSync(p));

function arg(name, dflt) {
  const i = process.argv.indexOf("--" + name);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : dflt;
}

const WORLD = arg("world", "wide1440");
const DIST = arg("dist", "/home/andrei/StorageGenie/frontend/dist");
const PORT = parseInt(arg("port", "5173"), 10);
const PAGE = arg("page", "/");
const SHOTS = arg("shots", "");
const OUT = arg("out", "");
const MASK_SELECTORS = arg("mask", "").split("|").filter(Boolean);
const BROWSER = arg("browser", "/home/andrei/.cache/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-linux64/chrome-headless-shell");
const TS = new Date().toISOString();

const WORLDS = {
  wide1440: {
    metrics: { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false, screenWidth: 1440, screenHeight: 900 },
    touch: false,
    toggle: true,
    expectDensity: "table",
  },
  touch390: {
    metrics: { width: 390, height: 844, deviceScaleFactor: 1, mobile: true, screenWidth: 390, screenHeight: 844 },
    touch: true,
    toggle: false,
    expectDensity: "grid",
  },
};
const W = WORLDS[WORLD];
if (!W) { log(`unknown world ${WORLD}`); process.exit(4); }

// ---------------------------------------------------------------- static server (SPA fallback, GET/HEAD only)
const MIME = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".mjs": "text/javascript",
  ".css": "text/css", ".json": "application/json", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
  ".png": "image/png", ".svg": "image/svg+xml", ".ico": "image/x-icon",
  ".woff": "font/woff", ".woff2": "font/woff2", ".map": "application/json",
};
const serverLog = { requests: [] };
let staticServer = null;
function startStatic() {
  return new Promise((resolve) => {
    staticServer = http.createServer((req, res) => {
      serverLog.requests.push({ method: req.method, url: req.url });
      if (req.method !== "GET" && req.method !== "HEAD") { res.writeHead(405); res.end("method not allowed"); return; }
      const urlPath = decodeURIComponent((req.url || "/").split("?")[0]);
      let filePath = join(DIST, urlPath);
      if (!filePath.startsWith(DIST)) { res.writeHead(403); res.end(); return; }
      if (!existsSync(filePath) || statSync(filePath).isDirectory()) filePath = join(DIST, "index.html");
      try {
        const body = readFileSync(filePath);
        res.writeHead(200, { "content-type": MIME[extname(filePath)] || "application/octet-stream" });
        res.end(body);
      } catch { res.writeHead(404); res.end("nf"); }
    });
    staticServer.listen(PORT, "127.0.0.1", () => resolve(PORT));
  });
}
function stopStatic() { return new Promise((r) => (staticServer ? staticServer.close(() => r()) : r())); }

// ---------------------------------------------------------------- CDP client (same shape as the frozen SG-208 driver)
class CDP {
  constructor(wsUrl) { this.ws = new WebSocket(wsUrl); this.id = 0; this.pending = new Map(); this.listeners = []; }
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

async function launchBrowser() {
  const userDir = `/tmp/opencode/sg212/profile-${WORLD}-${Date.now()}`;
  const browserHome = `/tmp/opencode/sg212/home`;
  mkdirSync(browserHome, { recursive: true });
  const args = [
    "--headless", "--no-sandbox", "--remote-debugging-port=0",
    `--user-data-dir=${userDir}`,
    "--no-first-run", "--no-default-browser-check", "--disable-gpu", "--disable-dev-shm-usage",
    "--force-device-scale-factor=1", "--window-size=1280,900",
    // keep the URL origin (CORS) as localhost:5173 while resolving to the loopback listener
    "--host-resolver-rules=MAP localhost 127.0.0.1",
    "about:blank",
  ];
  const child = spawn(BROWSER, args, { stdio: ["ignore", "ignore", "pipe"], env: { ...process.env, HOME: browserHome, XDG_CONFIG_HOME: browserHome + "/.config" } });
  child.stderr.on("data", (d) => { const s = d.toString(); if (/error/i.test(s) && !/DevTools listening|Failed to send GpuControl/.test(s)) log("browser stderr:", s.trim().slice(0, 300)); });
  const portFile = `${userDir}/DevToolsActivePort`;
  let port = 0; const deadline = Date.now() + 20000;
  while (Date.now() < deadline) {
    try { port = parseInt(readFileSync(portFile, "utf8").split("\n")[0], 10); if (port) break; } catch {}
    await sleep(150);
  }
  if (!port) { child.kill("SIGKILL"); throw new Error("browser did not expose DevToolsActivePort"); }
  const versionInfo = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
  return { child, port, userDir, args, versionInfo };
}

// ---------------------------------------------------------------- page scripts
const PROBE_JS = `(function(){
  var q = function(s){ return document.querySelector(s); };
  var contentEl = q('[data-testid="catalog-content-column"]');
  var scroller = q('[data-testid="table-scroll"]');
  var grid = q('[data-testid="catalog-grid"]');
  var buttons = Array.prototype.slice.call(document.querySelectorAll('[role="group"][aria-label="Density"] button'));
  var byName = function(name){ for (var i=0;i<buttons.length;i++){ if ((buttons[i].textContent||'').trim() === name) return buttons[i]; } return null; };
  var docEl = document.documentElement;
  var scroll = null;
  if (scroller) {
    var prev = scroller.scrollLeft;
    var max = scroller.scrollWidth - scroller.clientWidth;
    scroller.scrollLeft = 1e9;
    var reached = scroller.scrollLeft;
    scroller.scrollLeft = prev;
    scroll = { clientWidth: scroller.clientWidth, scrollWidth: scroller.scrollWidth, maxScrollLeft: max, reachedMax: reached, overflowX: getComputedStyle(scroller).overflowX };
  }
  var table = scroller ? scroller.querySelector('table') : null;
  var headers = table ? Array.prototype.map.call(table.querySelectorAll('thead th'), function(th){ return (th.textContent||'').trim(); }) : [];
  var all = document.querySelectorAll('*');
  var maxScrollLeftAnywhere = 0;
  var hScrollOffenders = [];
  for (var i=0;i<all.length;i++){
    var e = all[i]; var cs = getComputedStyle(e);
    var s = e.scrollWidth - e.clientWidth;
    if (s > 1 && cs.overflowX !== 'visible') {
      if (s > maxScrollLeftAnywhere) maxScrollLeftAnywhere = s;
      if (hScrollOffenders.length < 10) hScrollOffenders.push({ tag: e.tagName, testid: e.getAttribute('data-testid'), cls: String(e.className||'').slice(0,60), clientWidth: e.clientWidth, scrollWidth: e.scrollWidth, overflowX: cs.overflowX });
    }
  }
  return {
    url: location.href.split('?')[0],
    viewport: { innerWidth: window.innerWidth, innerHeight: window.innerHeight, dpr: window.devicePixelRatio },
    contentColumnPresent: !!contentEl,
    contentColumnWidth: contentEl ? contentEl.clientWidth : null,
    densityButtons: buttons.map(function(b){ return { label: (b.textContent||'').trim(), pressed: b.getAttribute('aria-pressed') }; }),
    gridPresent: !!grid,
    tablePresent: !!scroller,
    tableRows: document.querySelectorAll('[data-testid="product-row"]').length,
    tableHeaders: headers,
    itemCards: document.querySelectorAll('[data-testid="product-card"]').length,
    tableScroll: scroll,
    maxHScrollableWidth: maxScrollLeftAnywhere,
    hScrollOffenders: hScrollOffenders,
    docOverflowX: docEl.scrollWidth - docEl.clientWidth,
    alertsText: Array.prototype.map.call(document.querySelectorAll('[role="alert"]'), function(a){ return (a.textContent||'').trim().slice(0, 120); }),
    bodyTextLength: (document.body.innerText || '').length
  };
})()`;

const RECT_JS = (label) => `(function(){
  var buttons = Array.prototype.slice.call(document.querySelectorAll('[role="group"][aria-label="Density"] button'));
  for (var i=0;i<buttons.length;i++){
    if ((buttons[i].textContent||'').trim() === ${JSON.stringify(label)}) {
      var r = buttons[i].getBoundingClientRect();
      return { x: r.left + r.width/2, y: r.top + r.height/2, label: ${JSON.stringify(label)}, pressed: buttons[i].getAttribute('aria-pressed') };
    }
  }
  return null;
})()`;

function maskJs(selectors) {
  return `(function(){
    var sel = ${JSON.stringify(selectors)};
    var blockRun = function(len){ var out = ''; for (var i = 0; i < len; i++) out += '\\u25A0\\u200B'; return out; };
    var imgs = document.querySelectorAll("img, video, canvas");
    for (var i = 0; i < imgs.length; i++) imgs[i].style.filter = "blur(14px)";
    var masked = 0;
    for (var s = 0; s < sel.length; s++) {
      var nodes = document.querySelectorAll(sel[s]);
      for (var n = 0; n < nodes.length; n++) {
        var w = document.createTreeWalker(nodes[n], NodeFilter.SHOW_TEXT); var t;
        while ((t = w.nextNode())) { if (t.nodeValue && t.nodeValue.trim()) { t.nodeValue = blockRun(Math.min(t.nodeValue.trim().length, 40)); masked++; } }
      }
    }
    var sels = document.querySelectorAll("select");
    for (var q = 0; q < sels.length; q++) { for (var o = 0; o < sels[q].options.length; o++) { if (sels[q].options[o].text) { sels[q].options[o].text = blockRun(Math.min(sels[q].options[o].text.length, 40)); masked++; } } }
    var fields = document.querySelectorAll("input, textarea");
    for (var f = 0; f < fields.length; f++) { if (fields[f].value) { fields[f].value = blockRun(Math.min(fields[f].value.length, 40)); masked++; } }
    return { blurredImages: imgs.length, maskedTextNodes: masked, selectors: sel, blockRun: "U+25A0 + U+200B (layout-safe)" };
  })()`;
}

const redact = (url) => url.replace(/(household_id=)[^&]+/g, "$1<redacted>");

async function main() {
  const distFiles = ["index.html", ...readFileSync(join(DIST, "index.html"), "utf8").matchAll(/assets\/[^"]+/g)].map(String);
  const served = {};
  for (const f of distFiles) { const p = join(DIST, f.split("?")[0]); served[f] = { sha256: shaFile(p), bytes: statSync(p).size }; }

  await startStatic();
  log(`static server on 127.0.0.1:${PORT} serving ${DIST}`);
  const b = await launchBrowser();
  log(`browser pid ${b.child.pid}, DevTools port ${b.port} (${b.versionInfo["Browser"]})`);
  const cdp = new CDP(b.versionInfo.webSocketDebuggerUrl);
  await cdp.ready(); cdp.attach();
  const t = await cdp.send("Target.createTarget", { url: "about:blank" });
  const a = await cdp.send("Target.attachToTarget", { targetId: t.targetId, flatten: true });
  const sid = a.sessionId;
  await cdp.send("Page.enable", {}, sid);
  await cdp.send("Runtime.enable", {}, sid);
  await cdp.send("Network.enable", {}, sid);
  const netEvents = [];
  cdp.listeners.push((msg) => {
    if (msg.sessionId && msg.sessionId !== sid) return;
    const p = msg.params || {};
    if (msg.method === "Network.requestWillBeSent" && p.request) netEvents.push({ kind: "request", method: p.request.method, url: redact(String(p.request.url || "")) });
    if (msg.method === "Network.responseReceived") netEvents.push({ kind: "response", url: redact(String((p.response && p.response.url) || "")), status: p.response && p.response.status });
    if (msg.method === "Network.loadingFailed") netEvents.push({ kind: "failed", type: p.type, errorText: p.errorText });
    if (msg.method === "Runtime.consoleAPICalled") netEvents.push({ kind: "console", level: p.type, text: (p.args || []).map((x) => x.value ?? x.description ?? "").join(" ").slice(0, 300) });
    if (msg.method === "Runtime.exceptionThrown") netEvents.push({ kind: "exception", text: (p.exceptionDetails && ((p.exceptionDetails.exception && p.exceptionDetails.exception.description) || p.exceptionDetails.text)) || "" });
  });
  await cdp.send("Emulation.setDeviceMetricsOverride", W.metrics, sid);
  if (W.touch) await cdp.send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 5 }, sid);
  const url = `http://localhost:${PORT}${PAGE}`;
  await cdp.send("Page.navigate", { url }, sid);
  log(`navigated ${url} world=${WORLD}`);

  const evalJs = async (expr) => (await cdp.send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }, sid)).result.value;

  // Readiness is page-shaped: the Catalog must show real rows OR real cards (the
  // density decides which) — proves the SPA rendered and the API answered.
  const waitExpr = `document.querySelectorAll('[data-testid="product-row"], [data-testid="product-card"]').length > 0`;
  let ready = false; const readyDeadline = Date.now() + 45000;
  while (Date.now() < readyDeadline) {
    ready = await evalJs(waitExpr).catch(() => false);
    if (ready) break;
    await sleep(500);
  }
  log(`ready=${ready} at ${url}`);
  await sleep(2500);

  const probe1 = await evalJs(PROBE_JS);
  log(`probe1: ${JSON.stringify({ density: probe1.densityButtons, content: probe1.contentColumnWidth, rows: probe1.tableRows, cards: probe1.itemCards, docOverflowX: probe1.docOverflowX })}`);

  const mask = await evalJs(maskJs(MASK_SELECTORS));
  log(`mask: ${JSON.stringify(mask)}`);

  const shots = [];
  async function shoot(name) {
    if (!SHOTS) return;
    // Re-apply the mask before EVERY capture: a density toggle unmounts one
    // view and mounts the other, so name/img nodes created after the first
    // mask pass would otherwise reach the committed artifact unmasked.
    await evalJs(maskJs(MASK_SELECTORS));
    mkdirSync(SHOTS, { recursive: true });
    const cap = await cdp.send("Page.captureScreenshot", { format: "png" }, sid);
    const buf = Buffer.from(cap.data, "base64");
    const file = join(SHOTS, name);
    writeFileSync(file, buf);
    shots.push({ file, sha256: sha256(buf), bytes: buf.length });
    log(`screenshot ${file} ${shots[shots.length - 1].sha256} ${buf.length} B`);
  }
  async function clickButton(label) {
    const rect = await evalJs(RECT_JS(label));
    if (!rect) return { clicked: false, reason: "button not found" };
    await cdp.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: rect.x, y: rect.y }, sid);
    await cdp.send("Input.dispatchMouseEvent", { type: "mousePressed", x: rect.x, y: rect.y, button: "left", clickCount: 1 }, sid);
    await cdp.send("Input.dispatchMouseEvent", { type: "mouseReleased", x: rect.x, y: rect.y, button: "left", clickCount: 1 }, sid);
    await sleep(600);
    return { clicked: true, at: { x: Math.round(rect.x), y: Math.round(rect.y) }, wasPressed: rect.pressed };
  }

  const phases = { initial: { probe: probe1, shot: null }, toggle: [] };
  await shoot(`${WORLD}-initial-${W.expectDensity}.png`);
  if (shots.length) phases.initial.shot = shots[shots.length - 1];

  if (W.toggle) {
    for (const [label, expect] of [["Standard Grid", "grid"], ["Compact Table", "table"]]) {
      const click = await clickButton(label);
      const probe = await evalJs(PROBE_JS);
      await shoot(`${WORLD}-after-${expect}.png`);
      phases.toggle.push({ label, expect, click, probe, shot: shots[shots.length - 1] || null });
      log(`toggle -> ${expect}: ${JSON.stringify({ density: probe.densityButtons, grid: probe.gridPresent, table: probe.tablePresent, docOverflowX: probe.docOverflowX })}`);
    }
  }

  const densityPressed = (probe, label) => probe.densityButtons.some((x) => x.label === label && x.pressed === "true");
  const gate = { ready };
  if (WORLD === "wide1440") {
    gate.wideMeasure = probe1.contentColumnWidth >= 860;
    gate.opensInTable = densityPressed(probe1, "Compact Table") && probe1.tablePresent && !probe1.gridPresent && probe1.tableRows > 0 && !densityPressed(probe1, "Standard Grid");
    gate.tableNoScroll = !!probe1.tableScroll && probe1.tableScroll.maxScrollLeft === 0 && probe1.tableScroll.reachedMax === 0;
    gate.noDocOverflow = probe1.docOverflowX === 0;
    const toGrid = phases.toggle[0];
    const backToTable = phases.toggle[1];
    gate.toggleToGrid = !!toGrid && toGrid.click.clicked && densityPressed(toGrid.probe, "Standard Grid") && toGrid.probe.gridPresent && !toGrid.probe.tablePresent && toGrid.probe.docOverflowX === 0;
    gate.toggleBackToTable = !!backToTable && backToTable.click.clicked && densityPressed(backToTable.probe, "Compact Table") && backToTable.probe.tablePresent && !backToTable.probe.gridPresent && backToTable.probe.tableScroll && backToTable.probe.tableScroll.maxScrollLeft === 0;
  } else {
    gate.narrowMeasure = probe1.contentColumnWidth > 0 && probe1.contentColumnWidth < 860;
    gate.opensInGrid = densityPressed(probe1, "Standard Grid") && probe1.gridPresent && !probe1.tablePresent && probe1.itemCards > 0 && !densityPressed(probe1, "Compact Table");
    gate.noDocOverflow = probe1.docOverflowX === 0;
  }
  gate.noAlerts = probe1.alertsText.length === 0;
  const apiRequests = netEvents.filter((e) => e.kind === "request" && e.url.includes(":8003/"));
  const apiNonGet = apiRequests.filter((e) => e.method !== "GET" && e.method !== "HEAD" && e.method !== "OPTIONS");
  const exceptions = netEvents.filter((e) => e.kind === "exception");
  gate.noNonGet = apiNonGet.length === 0;
  gate.noExceptions = exceptions.length === 0;
  const pass = Object.values(gate).every(Boolean);

  const out = { ts: TS, world: WORLD, emulation: { metrics: W.metrics, touch: W.touch }, url, browser: b.versionInfo.Browser, staticRequests: serverLog.requests, served, probe1, phases, apiRequests, apiNonGet, exceptions, mask, gate, pass, shots };
  if (OUT) { mkdirSync(dirname(OUT), { recursive: true }); writeFileSync(OUT, JSON.stringify(out, null, 2)); }

  b.child.kill("SIGKILL");
  await sleep(300);
  await stopStatic();
  process.stdout.write(JSON.stringify({ ts: TS, world: WORLD, url, gate, pass, shots, served }, null, 2) + "\n");
  process.exit(pass ? 0 : 3);
}

main().catch((e) => { log("FATAL", (e && e.stack) || String(e)); process.exit(4); });
