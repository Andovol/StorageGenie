#!/usr/bin/env node
// SG-207 served-Catalog drawer smoke driver (dependency-free; Node >= 22 built-in WebSocket).
// Purpose (packet G2/A2): serve the CANDIDATE frontend/dist on 127.0.0.1:5173 — the origin
// the backend's CORS allow-list carries at serve time (backend/app/config.py:19 reads
// CORS_ORIGINS=http://localhost:5173, measured via `docker exec … printenv`) — then drive
// chrome-headless-shell through raw CDP: navigate /catalog, click the first product card,
// wait for the inspector drawer, and assert that the D-12 removal holds ON THE SERVED PAGE:
// no [data-testid="raw-json"] node, no <pre>, no button whose accessible name matches
// /raw\s*data/i, while the drawer's Metadata / Observed (read-only) / AI actions sections and
// its editable inputs are present (non-vacuity: the drawer is the real one, not an empty shell).
// Privacy (CO-44, SG-205 precedent): masking runs AFTER all assertions and BEFORE the single
// screenshot — images blurred, asset names/categories/descriptions and editable values masked.
// Read-only: the page performs GETs only (react-query mounts); no form is submitted.
// No interactive prompt; every wait is bounded; browser exits with the run.
//
// Usage: node SG-207_driver.mjs --dist <frontend/dist> --shot <png path> --out <json path>
// Machine summary on stdout (CO-93); progress on stderr.

import { spawn } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync } from "node:fs";
import { extname, join, dirname } from "node:path";
import http from "node:http";
import crypto from "node:crypto";

function log(...a) { console.error("[sg207]", ...a); }
function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }
function sha256(buf) { return crypto.createHash("sha256").update(buf).digest("hex"); }
const shaFile = (p) => sha256(readFileSync(p));

function arg(name, dflt) {
  const i = process.argv.indexOf("--" + name);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : dflt;
}

const DIST = arg("dist", "/home/andrei/StorageGenie/frontend/dist");
const PORT = parseInt(arg("port", "5173"), 10);
const PAGE = arg("page", "/");
const SHOT = arg("shot", "");
const OUT = arg("out", "");
const BROWSER = arg("browser", "/home/andrei/.cache/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-linux64/chrome-headless-shell");
const TS = new Date().toISOString();

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

// ---------------------------------------------------------------- CDP client (same shape as the frozen SG-205 driver)
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
  const userDir = `/tmp/opencode/sg207/profile-${Date.now()}`;
  const browserHome = "/tmp/opencode/sg207/home";
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
const CLICK_FIRST_CARD_JS = `(function(){
  var cards = document.querySelectorAll('[data-testid="product-card"]');
  if (!cards.length) return { clicked: false, cards: 0 };
  var name = (cards[0].textContent || "").trim().slice(0, 60);
  cards[0].click();
  return { clicked: true, cards: cards.length, firstCardTextLen: name.length };
})()`;

const ASSERT_JS = `(function(){
  var d = document.querySelector('[data-testid="inspector-drawer"]');
  var q = function(sel){ return d ? d.querySelectorAll(sel) : null; };
  var btnNames = d ? Array.prototype.map.call(d.querySelectorAll("button"), function(b){ return ((b.getAttribute("aria-label") || "") + " " + (b.textContent || "")).trim(); }) : [];
  return {
    drawerPresent: !!d,
    drawerRole: d ? d.getAttribute("role") : null,
    drawerAriaLabel: d ? d.getAttribute("aria-label") : null,
    titleText: d && d.querySelector('[data-testid="drawer-title"]') ? d.querySelector('[data-testid="drawer-title"]').textContent : null,
    headings: d ? Array.prototype.map.call(d.querySelectorAll("h3"), function(h){ return h.textContent; }) : null,
    labels: d ? Array.prototype.map.call(d.querySelectorAll("label"), function(l){ return l.textContent; }) : null,
    inputCount: d ? d.querySelectorAll("input").length : null,
    buttonNames: btnNames,
    rawJsonNodes: d ? q('[data-testid="raw-json"]').length : null,
    preNodes: d ? q("pre").length : null,
    rawDataButtons: d ? Array.prototype.filter.call(d.querySelectorAll("button"), function(b){ return /raw\\s*data/i.test(b.getAttribute("aria-label") || b.textContent || ""); }).length : null,
    bodyTextMatchesRawData: /raw\\s*data/i.test(document.body.innerText || document.body.textContent || ""),
    sourceState: d ? (d.querySelector('[data-testid="source-image"]') ? "source-image" : (d.querySelector('[data-testid="source-empty"]') ? "source-empty" : "none")) : null,
    hasSaveButton: d ? Array.prototype.some.call(d.querySelectorAll("button"), function(b){ return /save changes/i.test(b.textContent || ""); }) : null,
    hasAiButtons: d ? Array.prototype.filter.call(d.querySelectorAll("button"), function(b){ return /re-isolate asset|generate context scene/i.test(b.textContent || ""); }).length : null,
    drawerTextTail: d ? (d.innerText || d.textContent || "").trim().slice(-200) : null
  };
})()`;

const MASK_JS = `(function(){
  var blockRun = function(len){ var out = ''; for (var i = 0; i < len; i++) out += '\\u25A0\\u200B'; return out; };
  var maskEl = function(el){ if (!el) return 0; var t = (el.textContent || ""); if (!t.trim()) return 0; el.textContent = blockRun(Math.min(t.trim().length, 60)); return 1; };
  var imgs = document.querySelectorAll("img, video, canvas");
  for (var i = 0; i < imgs.length; i++) imgs[i].style.filter = "blur(14px)";
  var masked = 0;
  var drawer = document.querySelector('[data-testid="inspector-drawer"]');
  if (drawer) {
    masked += maskEl(drawer.querySelector('[data-testid="drawer-title"]'));
    masked += maskEl(drawer.querySelector('[data-testid="drawer-category"]'));
    masked += maskEl(drawer.querySelector('[data-testid="drawer-description"]'));
    var fields = drawer.querySelectorAll("input, textarea");
    for (var f = 0; f < fields.length; f++) { if (fields[f].value) { fields[f].value = blockRun(Math.min(fields[f].value.length, 60)); masked++; } }
  }
  var cards = document.querySelectorAll('[data-testid="product-card"]');
  for (var c = 0; c < cards.length; c++) {
    var walker = document.createTreeWalker(cards[c], NodeFilter.SHOW_TEXT);
    var t;
    while ((t = walker.nextNode())) { if (t.nodeValue && t.nodeValue.trim()) { t.nodeValue = blockRun(Math.min(t.nodeValue.trim().length, 40)); masked++; } }
  }
  var sel = document.querySelector("select");
  if (sel) { for (var o = 0; o < sel.options.length; o++) { if (sel.options[o].text) { sel.options[o].text = blockRun(Math.min(sel.options[o].text.length, 40)); masked++; } } }
  return { blurredImages: imgs.length, maskedTextNodes: masked, blockRun: "U+25A0 + U+200B (layout-safe)" };
})()`;

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
    if (msg.method === "Network.responseReceived") netEvents.push({ kind: "response", url: p.response && p.response.url, status: p.response && p.response.status });
    if (msg.method === "Network.loadingFailed") netEvents.push({ kind: "failed", type: p.type, errorText: p.errorText });
    if (msg.method === "Runtime.consoleAPICalled") netEvents.push({ kind: "console", level: p.type, text: (p.args || []).map((a) => a.value ?? a.description ?? "").join(" ").slice(0, 300) });
    if (msg.method === "Runtime.exceptionThrown") netEvents.push({ kind: "exception", text: (p.exceptionDetails && ((p.exceptionDetails.exception && p.exceptionDetails.exception.description) || p.exceptionDetails.text)) || "" });
  });
  await cdp.send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false, screenWidth: 1280, screenHeight: 900 }, sid);
  const url = `http://localhost:${PORT}${PAGE}`;
  await cdp.send("Page.navigate", { url }, sid);
  log(`navigated ${url}`);

  const evalJs = async (expr) => (await cdp.send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }, sid)).result.value;

  let cards = 0; const cardDeadline = Date.now() + 45000;
  while (Date.now() < cardDeadline) {
    cards = await evalJs(`document.querySelectorAll('[data-testid="product-card"]').length`).catch(() => 0);
    if (cards > 0) break;
    await sleep(500);
  }
  log(`product cards on served Catalog: ${cards}`);
  const click = await evalJs(CLICK_FIRST_CARD_JS);
  log(`click: ${JSON.stringify(click)}`);

  let drawer = false; const drawerDeadline = Date.now() + 20000;
  while (Date.now() < drawerDeadline) {
    drawer = await evalJs(`!!document.querySelector('[data-testid="inspector-drawer"]')`).catch(() => false);
    if (drawer) break;
    await sleep(300);
  }
  await sleep(2000);
  const assertions = await evalJs(ASSERT_JS);
  log(`assertions: ${JSON.stringify(assertions)}`);
  const pageState = {
    locationHref: await evalJs("location.href").catch(() => null),
    bodyText: (await evalJs("(document.body.innerText || '').slice(0, 1500)").catch(() => null)),
    rootChildren: await evalJs("document.getElementById('root') ? document.getElementById('root').children.length : -1").catch(() => null),
  };
  log(`pageState: ${JSON.stringify(pageState)}`);
  log(`netEvents: ${JSON.stringify(netEvents.slice(0, 40))}`);

  const mask = await evalJs(MASK_JS);
  log(`mask: ${JSON.stringify(mask)}`);

  // bring the drawer's END into the viewport so the screenshot shows the region the removed
  // panel used to occupy (pre-change the collapse toggle sat after the AI actions section)
  const scrolled = await evalJs(`(function(){ var d = document.querySelector('[data-testid="inspector-drawer"] [role="dialog"]'); if (!d) return null; d.scrollTop = d.scrollHeight; return { scrollTop: d.scrollTop, scrollHeight: d.scrollHeight, clientHeight: d.clientHeight }; })()`);
  log(`drawer scrolled to end: ${JSON.stringify(scrolled)}`);
  await sleep(500);

  let shot = null;
  if (SHOT) {
    mkdirSync(dirname(SHOT), { recursive: true });
    const cap = await cdp.send("Page.captureScreenshot", { format: "png" }, sid);
    const buf = Buffer.from(cap.data, "base64");
    writeFileSync(SHOT, buf);
    shot = { file: SHOT, sha256: sha256(buf), bytes: buf.length };
    log(`screenshot ${SHOT} ${shot.sha256} ${shot.bytes} B`);
  }

  const gate = {
    drawerPresent: assertions.drawerPresent === true,
    noRawJsonNode: assertions.rawJsonNodes === 0,
    noPreNode: assertions.preNodes === 0,
    noRawDataButton: assertions.rawDataButtons === 0,
    bodyHasNoRawDataText: assertions.bodyTextMatchesRawData === false,
    sectionsIntact: JSON.stringify(assertions.headings) === JSON.stringify(["Metadata", "Observed (read-only)", "AI actions"]),
    editableInputs: assertions.inputCount === 5,
    aiButtonsPresent: assertions.hasAiButtons === 2,
  };
  const pass = Object.values(gate).every(Boolean);

  const out = { ts: TS, url, released: { cdpTarget: t.targetId, browser: b.versionInfo.Browser }, userDataDir: b.userDir, staticRequests: serverLog.requests, served, cards, click, assertions, pageState, netEvents, scrolled, mask, gate, pass, shot };
  if (OUT) { mkdirSync(dirname(OUT), { recursive: true }); writeFileSync(OUT, JSON.stringify(out, null, 2)); }

  b.child.kill("SIGKILL");
  await sleep(300);
  await stopStatic();
  process.stdout.write(JSON.stringify({ ts: TS, url, cards, gate, pass, shot: shot ? { file: shot.file, sha256: shot.sha256, bytes: shot.bytes } : null, served, pageState, netEvents: netEvents.slice(0, 40) }, null, 2) + "\n");
  process.exit(pass ? 0 : 3);
}

main().catch((e) => { log("FATAL", e && e.stack || String(e)); process.exit(4); });
