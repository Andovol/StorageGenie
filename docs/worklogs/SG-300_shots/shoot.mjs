// SG-300 scratch only: screenshots through the Chrome DevTools Protocol (Node built-in WebSocket, no packages).
// Runs from the repo root. Writes docs/worklogs/SG-300_shots/*.png and proof.json.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const OUT = "docs/worklogs/SG-300_shots";
const PROFILE = "output/SG-300-scratch/chrome-profile";
const F = "http://127.0.0.1:14300";
const API = "http://127.0.0.1:18300";
const MILK = "01a1c761-be19-7880-9fc9-b2eee3e5ff76";
const JUICE = "01a1c761-bdef-7dd0-81cb-076c76aeae7d";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

fs.mkdirSync(OUT, { recursive: true });
const [port, wsPath] = fs.readFileSync(path.join(PROFILE, "DevToolsActivePort"), "utf8").split("\n");
const ws = new WebSocket(`ws://127.0.0.1:${port.trim()}${wsPath.trim()}`);
let seq = 0;
const pending = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const { res, rej } = pending.get(m.id);
    pending.delete(m.id);
    if (m.error) rej(new Error(JSON.stringify(m.error)));
    else res(m.result);
  }
};
const send = (method, params = {}, sessionId) =>
  new Promise((res, rej) => {
    const id = ++seq;
    pending.set(id, { res, rej });
    ws.send(JSON.stringify({ id, method, params, sessionId }));
  });
await new Promise((r) => (ws.onopen = r));
const { targetId } = await send("Target.createTarget", { url: "about:blank" });
const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
const S = (m, p) => send(m, p, sessionId);
await S("Page.enable");
await S("Runtime.enable");

async function evalJs(expr) {
  const r = await S("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 300));
  return r.result.value;
}
async function waitFor(expr, ms = 25000) {
  const t = Date.now();
  while (Date.now() - t < ms) {
    const v = await evalJs(expr).catch(() => null);
    if (v) return v;
    await sleep(250);
  }
  throw new Error("timeout waiting for: " + expr);
}
async function viewport(w, h, dark) {
  await S("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: w < 500 });
  await S("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: dark ? "dark" : "light" }] });
  await sleep(400);
}
async function goto(url, readyExpr) {
  await S("Page.navigate", { url });
  await waitFor(readyExpr);
  await sleep(600);
}
async function shot(name, full = false) {
  const params = { format: "png" };
  if (full) {
    const m = await S("Page.getLayoutMetrics", {});
    const cs = m.cssContentSize;
    params.captureBeyondViewport = true;
    params.clip = { x: 0, y: 0, width: Math.ceil(cs.width), height: Math.ceil(cs.height), scale: 1 };
  }
  const { data } = await S("Page.captureScreenshot", params);
  const buf = Buffer.from(data, "base64");
  fs.writeFileSync(path.join(OUT, name + ".png"), buf);
  return { name, sha12: crypto.createHash("sha256").update(buf).digest("hex").slice(0, 12), bytes: buf.length };
}
const hhList = await (await fetch(`${API}/v1/households`)).json();
const HH = (Array.isArray(hhList) ? hhList : hhList.items)[0].id;
const PANTRY_READY = "!!document.querySelector('[data-testid=pantry-grid]')";
const results = [];
const proof = {};
const clickByText = (sel, text) =>
  `(() => { const el = [...document.querySelectorAll(${JSON.stringify(sel)})].find(e => e.textContent.trim() === ${JSON.stringify(text)}); if (!el) return false; el.click(); return true; })()`;
const layout = `(() => { const tiles=[...document.querySelectorAll('[data-testid=pantry-grid] > article')]; const cols=new Set(tiles.map(t=>t.offsetLeft)).size; return { cols, scrollOverflow: document.documentElement.scrollWidth - window.innerWidth, bodyBg: getComputedStyle(document.body).backgroundColor, tiles: tiles.length, borderedWrappers: tiles.filter(t=>getComputedStyle(t).borderTopStyle!=='none' && getComputedStyle(t).borderTopWidth!=='0px').length }; })()`;

// --- light and dark, Pantry full page and Use soon, 1280 and 375
await viewport(1280, 800, false);
await goto(`${F}/pantry`, PANTRY_READY);
proof.layout1280 = await evalJs(layout);
proof.count = await evalJs("document.querySelector('[data-testid=pantry-count]').textContent");
results.push(await shot("pantry-full-light-1280", true));
results.push(await shot("pantry-useseen-light-1280", false));
proof.useSoonText1280 = await evalJs("document.querySelector('[data-testid=pantry-use-soon-grid]')?.textContent ?? 'NONE'");
proof.expiredLabel = await evalJs("[...document.querySelectorAll('[data-testid=pantry-expired]')].map(e=>e.textContent)");

await viewport(375, 812, false);
await sleep(400);
proof.layout375 = await evalJs(layout);
results.push(await shot("pantry-full-light-375", true));
results.push(await shot("pantry-useseen-light-375", false));
proof.useSoonText375 = await evalJs("document.querySelector('[data-testid=pantry-use-soon-grid]')?.textContent ?? 'NONE'");

// --- a tile after -1 (made through the API before the shot)
const dec = await fetch(`${API}/v1/assets/${MILK}/quantity/decrement?household_id=${HH}`, { method: "POST", headers: { "content-type": "application/json" } });
proof.decrementStatus = dec.status;
await goto(`${F}/pantry`, PANTRY_READY);
await waitFor(`!!document.querySelector('[data-asset-id="${MILK}"] [data-testid=pantry-quantity]') && document.querySelector('[data-asset-id="${MILK}"] [data-testid=pantry-quantity]').textContent.includes('1 left')`);
await evalJs(`document.querySelector('[data-asset-id="${MILK}"]').scrollIntoView({block:'center'})`);
await sleep(300);
proof.milkTile = await evalJs(`document.querySelector('[data-asset-id="${MILK}"]').textContent`);
results.push(await shot("pantry-tileminus-375", false));

// --- the notice after Use it up (click), then Put back (click) and the tile returns
await evalJs(`document.querySelector('[data-asset-id="${JUICE}"]').scrollIntoView({block:'center'})`);
await sleep(300);
const clicked = await evalJs(`(() => { const t = document.querySelector('[data-asset-id="${JUICE}"]'); const b = [...t.querySelectorAll('button')].find(x => x.textContent.trim() === 'Use it up'); if (!b) return false; b.click(); return true; })()`);
proof.useItUpClicked = clicked;
await waitFor("!!document.querySelector('[data-testid=pantry-notice]')");
proof.noticeText = await evalJs("document.querySelector('[data-testid=pantry-notice]').textContent");
results.push(await shot("pantry-notice-375", false));
await evalJs(`(() => { const n = document.querySelector('[data-testid=pantry-notice]'); const b = [...n.querySelectorAll('button')].find(x => x.textContent.trim() === 'Put back'); b.click(); return true; })()`);
await waitFor(`!!document.querySelector('[data-asset-id="${JUICE}"]')`);
proof.putBackRestoredJuice = true;

// --- item panel showing "1 left" (1280)
await viewport(1280, 800, false);
await goto(`${F}/pantry`, PANTRY_READY);
await evalJs(clickByText("button", "") ? `(() => { const b=[...document.querySelectorAll('button[aria-label="Open Milk"]')][0]; b.click(); return true; })()` : "false");
await waitFor("!!document.querySelector('[aria-label=\"Amount left\"]') && document.querySelector('[aria-label=\"Amount left\"]').textContent.includes('left')");
await sleep(500);
proof.panelText = await evalJs("document.querySelector('[aria-label=\"Amount left\"]').textContent");
results.push(await shot("item-panel-light-1280", false));

// --- catalog Gone view (1280)
await goto(`${F}/`, "!!document.body && document.body.textContent.length > 200");
const toggled = await evalJs(`(() => { const el=[...document.querySelectorAll('button,a,[role=tab],[role=button]')].find(e => /^Gone$/.test(e.textContent.trim())); if(!el) return 'no Gone control'; el.click(); return 'clicked'; })()`);
proof.catalogGoneControl = toggled;
await sleep(1200);
proof.catalogGoneText = await evalJs("document.body.textContent.includes('Old Soup') ? 'Old Soup listed' : 'Old Soup NOT listed'");
results.push(await shot("catalog-gone-light-1280", false));

// --- dark: full page 1280 and 375, Use soon 375
await viewport(1280, 800, true);
await goto(`${F}/pantry`, PANTRY_READY);
proof.layoutDark1280 = await evalJs(layout);
results.push(await shot("pantry-full-dark-1280", true));
await viewport(375, 812, true);
await sleep(400);
results.push(await shot("pantry-full-dark-375", true));
results.push(await shot("pantry-useseen-dark-375", false));
proof.darkBg375 = await evalJs(layout);

fs.writeFileSync(path.join(OUT, "proof.json"), JSON.stringify({ results, proof }, null, 2));
console.log(JSON.stringify({ results, proof }, null, 2));
ws.close();
process.exit(0);
