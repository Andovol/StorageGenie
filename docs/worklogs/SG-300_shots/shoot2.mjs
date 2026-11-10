// SG-300 scratch only: mode "catalog" (DOM proof of the Gone view) or "empty" (Pantry empty state, 375 px).
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const mode = process.argv[2];
const OUT = "docs/worklogs/SG-300_shots";
const PROFILE = "output/SG-300-scratch/chrome-profile";
const F = "http://127.0.0.1:14300";
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

if (mode === "catalog") {
  await viewport(1280, 800, false);
  await S("Page.navigate", { url: `${F}/` });
  await waitFor("document.body.textContent.includes('Loaded')");
  const clicked = await evalJs(`(() => { const el=[...document.querySelectorAll('button,a,[role=tab],[role=button]')].find(e => /^Gone$/.test(e.textContent.trim())); if(!el) return false; el.click(); return true; })()`);
  await waitFor("[...document.querySelectorAll('*')].some(e => e.childElementCount === 0 && e.textContent.trim() === 'Gone — used up')");
  const proof = {
    clicked,
    goneLine: await evalJs("[...document.querySelectorAll('*')].filter(e => e.childElementCount === 0 && e.textContent.trim() === 'Gone — used up').map(e => e.textContent.trim())"),
    oldSoupLink: await evalJs("[...document.querySelectorAll('a')].filter(a => a.textContent.trim() === 'Old Soup').length"),
    putBackButton: await evalJs("[...document.querySelectorAll('button')].filter(b => b.textContent.trim() === 'Put back').length"),
  };
  console.log(JSON.stringify(proof));
} else if (mode === "empty") {
  await viewport(375, 812, false);
  await S("Page.navigate", { url: `${F}/pantry` });
  await waitFor("document.body.textContent.includes('No food yet')");
  await sleep(600);
  const proof = {
    count: await evalJs("document.querySelector('[data-testid=pantry-count]')?.textContent ?? 'NONE'"),
    emptyStatus: await evalJs("[...document.querySelectorAll('[role=status]')].map(e=>e.textContent)"),
    useSoon: await evalJs("[...document.querySelectorAll('section[aria-label=\"Use soon\"]')].map(e=>e.textContent)"),
    scrollOverflow: await evalJs("document.documentElement.scrollWidth - window.innerWidth"),
  };
  const { data } = await S("Page.captureScreenshot", { format: "png" });
  const buf = Buffer.from(data, "base64");
  fs.writeFileSync(path.join(OUT, "pantry-empty-375.png"), buf);
  proof.sha12 = crypto.createHash("sha256").update(buf).digest("hex").slice(0, 12);
  proof.bytes = buf.length;
  console.log(JSON.stringify(proof));
}
ws.close();
process.exit(0);
