#!/usr/bin/env node
// SG-208 served-UI smoke driver (dependency-free; Node >= 22 built-in WebSocket).
// Purpose (packet G2/A1): serve the CANDIDATE frontend/dist on 127.0.0.1:5173 — the
// origin the backend's CORS allow-list carries (backend/app/config.py:19) — then drive
// chrome-headless-shell through raw CDP: navigate the given route and assert that the
// D-13 removal holds ON THE SERVED PAGE: zero <select> whose accessible name matches
// /household/i, no `aria-label="Household"` markup, no "Select household"/"No households"
// option copy, while the page's own selects render (non-vacuity: the combobox scan runs
// on a DOM that HAS selects) and the household-scoped API reads fired by the page carry
// `household_id=` (readback, not code-reading).
// Privacy (CO-44, SG-205/SG-207 precedent): masking runs AFTER all measurement and BEFORE
// the single screenshot; household_id query VALUES are redacted in the committed JSON
// (the seeded household name never enters any artifact). Read-only: the page performs GETs
// only; no form is submitted. No interactive prompt; every wait is bounded; browser exits
// with the run.
//
// Usage: node SG-208_driver.mjs --dist <frontend/dist> --page / --shot <png> --out <json> [--mask 'sel1|sel2']
// Machine summary on stdout (CO-93); progress on stderr.

import { spawn } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync } from "node:fs";
import { extname, join, dirname } from "node:path";
import http from "node:http";
import crypto from "node:crypto";

function log(...a) { console.error("[sg208]", ...a); }
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
const MASK_SELECTORS = arg("mask", "").split("|").filter(Boolean);
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

// ---------------------------------------------------------------- CDP client (same shape as the frozen SG-207 driver)
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
  const userDir = `/tmp/opencode/sg208/profile-${Date.now()}`;
  const browserHome = "/tmp/opencode/sg208/home";
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
const GATE_JS = `(function(){
  function nameOf(sel){
    var n = sel.getAttribute("aria-label") || "";
    if (!n) { var l = sel.closest("label"); if (l) n = (l.textContent || "").trim(); }
    if (!n) { var id = sel.getAttribute("id"); if (id) { var l2 = document.querySelector('label[for="' + id + '"]'); if (l2) n = (l2.textContent || "").trim(); } }
    return n.slice(0, 60);
  }
  var selects = Array.prototype.map.call(document.querySelectorAll("select"), function(s){ return { name: nameOf(s), options: s.options.length }; });
  var html = document.documentElement.outerHTML;
  var headings = Array.prototype.map.call(document.querySelectorAll("h1, h2"), function(h){ return (h.textContent || "").trim().slice(0, 40); });
  return {
    selectCount: selects.length,
    selectNames: selects.map(function(s){ return s.name; }),
    householdSelectCount: selects.filter(function(s){ return /household/i.test(s.name); }).length,
    ariaHouseholdPresent: html.indexOf('aria-label="Household"') !== -1,
    selectHouseholdTextPresent: html.indexOf("Select household") !== -1 || html.indexOf("No households") !== -1,
    bodyHasHouseholdWord: /\\bhousehold\\b/i.test(document.body.innerText || ""),
    productCards: document.querySelectorAll('[data-testid="product-card"]').length,
    headingTexts: headings,
    reviewStatusSelect: selects.some(function(s){ return /review status/i.test(s.name); }),
    alertsText: Array.prototype.map.call(document.querySelectorAll('[role="alert"]'), function(a){ return (a.textContent || "").trim().slice(0, 120); }),
    bodyTextLength: (document.body.innerText || "").length
  };
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
  await cdp.send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false, screenWidth: 1280, screenHeight: 900 }, sid);
  const url = `http://localhost:${PORT}${PAGE}`;
  await cdp.send("Page.navigate", { url }, sid);
  log(`navigated ${url}`);

  const evalJs = async (expr) => (await cdp.send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }, sid)).result.value;

  // Readiness is page-shaped: Catalog must show real cards; Inbox must show its h1 + its
  // own combobox (Review status). Both prove the SPA rendered, so the scan below is live.
  const waitExpr = PAGE === "/"
    ? `document.querySelectorAll('[data-testid="product-card"]').length > 0`
    : `(function(){ return document.querySelector('h1') !== null && document.querySelectorAll('select').length > 0; })()`;
  let ready = false; const readyDeadline = Date.now() + 45000;
  while (Date.now() < readyDeadline) {
    ready = await evalJs(waitExpr).catch(() => false);
    if (ready) break;
    await sleep(500);
  }
  log(`ready=${ready} at ${url}`);
  await sleep(2500);

  const assertions = await evalJs(GATE_JS);
  log(`assertions: ${JSON.stringify(assertions)}`);

  const mask = await evalJs(maskJs(MASK_SELECTORS));
  log(`mask: ${JSON.stringify(mask)}`);

  let shot = null;
  if (SHOT) {
    mkdirSync(dirname(SHOT), { recursive: true });
    const cap = await cdp.send("Page.captureScreenshot", { format: "png" }, sid);
    const buf = Buffer.from(cap.data, "base64");
    writeFileSync(SHOT, buf);
    shot = { file: SHOT, sha256: sha256(buf), bytes: buf.length };
    log(`screenshot ${SHOT} ${shot.sha256} ${shot.bytes} B`);
  }

  // Scoped-read readback: the served page's own GETs to the live API must carry
  // household_id (values redacted in the JSON) and succeed (200).
  const apiRequests = netEvents.filter((e) => e.kind === "request" && e.url.includes(":8003/"));
  const apiResponses = netEvents.filter((e) => e.kind === "response" && e.url.includes(":8003/"));
  const scopedRequests = apiRequests.filter((e) => e.url.includes("household_id="));
  const scopedOk = apiResponses.filter((e) => e.url.includes("household_id=") && e.status === 200);

  const gate = {
    noHouseholdSelect: assertions.householdSelectCount === 0 && assertions.ariaHouseholdPresent === false && assertions.selectHouseholdTextPresent === false,
    noHouseholdWordOnPage: assertions.bodyHasHouseholdWord === false,
    selectScanLive: assertions.selectCount >= 1,
    scopedReads: scopedRequests.length >= 2 && scopedOk.length >= 2,
    pageRendered: PAGE === "/" ? assertions.productCards > 0 : (assertions.headingTexts.indexOf("Inbox") !== -1 && assertions.reviewStatusSelect === true),
  };
  const pass = ready && Object.values(gate).every(Boolean);

  const out = { ts: TS, url, page: PAGE, browser: b.versionInfo.Browser, staticRequests: serverLog.requests, served, assertions, apiRequests, apiResponses, scopedRequestCount: scopedRequests.length, scopedOkCount: scopedOk.length, mask, gate, pass, shot };
  if (OUT) { mkdirSync(dirname(OUT), { recursive: true }); writeFileSync(OUT, JSON.stringify(out, null, 2)); }

  b.child.kill("SIGKILL");
  await sleep(300);
  await stopStatic();
  process.stdout.write(JSON.stringify({ ts: TS, url, page: PAGE, gate, pass, shot, served, assertions: { ...assertions }, scopedRequestCount: scopedRequests.length, scopedOkCount: scopedOk.length }, null, 2) + "\n");
  process.exit(pass ? 0 : 3);
}

main().catch((e) => { log("FATAL", (e && e.stack) || String(e)); process.exit(4); });
