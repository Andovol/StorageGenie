// SG-300 scratch only: test data through the API on 127.0.0.1:18300. Providers are off (fake).
import zlib from "node:zlib";

const B = "http://127.0.0.1:18300";
const mode = process.argv[2] ?? "full"; // "full" or "empty"

function crcTable() {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
}
const T = crcTable();
function crc32(buf) {
  let c = 0xffffffff;
  for (const b of buf) c = T[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
function chunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length);
  const td = Buffer.concat([Buffer.from(type), data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(td));
  return Buffer.concat([len, td, crc]);
}
// A generated 96x96 test image: a colour field with a lighter disc (no real photo).
function png(hue) {
  const w = 96, h = 96;
  const raw = Buffer.alloc((w * 3 + 1) * h);
  for (let y = 0; y < h; y++) {
    raw[y * (w * 3 + 1)] = 0;
    for (let x = 0; x < w; x++) {
      const d = Math.hypot(x - 48, y - 48) < 26;
      const o = y * (w * 3 + 1) + 1 + x * 3;
      raw[o] = d ? 245 : (hue * 37) % 200;
      raw[o + 1] = d ? 235 : (hue * 71 + y) % 180;
      raw[o + 2] = d ? 210 : (hue * 53 + x) % 160;
    }
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0);
  ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 2; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  return Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    chunk("IHDR", ihdr),
    chunk("IDAT", zlib.deflateSync(raw)),
    chunk("IEND", Buffer.alloc(0)),
  ]);
}

async function call(method, url, body, headers = {}) {
  const r = await fetch(B + url, {
    method,
    headers: { "content-type": "application/json", ...headers },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await r.text();
  if (!r.ok) throw new Error(`${method} ${url} -> ${r.status} ${text.slice(0, 300)}`);
  return text ? JSON.parse(text) : null;
}

const hh = await call("POST", "/v1/households", { name: "Home" });
console.log("household", hh.id);
if (mode === "empty") {
  console.log("empty household ready");
  process.exit(0);
}
const H = `household_id=${hh.id}`;

async function evidence(hue) {
  const form = new FormData();
  form.append("file", new Blob([png(hue)], { type: "image/png" }), `test-${hue}.png`);
  const r = await fetch(`${B}/v1/evidence?${H}`, { method: "POST", body: form });
  if (!r.ok) throw new Error(`evidence ${r.status} ${await r.text()}`);
  return (await r.json()).id;
}

// name, quantity, unit, expiry (YYYY-MM-DD) or null, gone?, unsorted?, hue
const items = [
  ["Cheese", 1, "pcs", "2026-11-09", false, false, 1],
  ["Juice", 500, "ml", "2026-11-07", false, false, 2],
  ["Milk", 2, "pcs", "2026-11-11", false, false, 3],
  ["Yogurt", 1, "pcs", "2026-11-12", false, false, 4],
  ["Apples", 4, "", "2026-11-13", false, false, 5],
  ["Eggs", 6, "pcs", "2026-11-15", false, false, 6],
  ["Bread", 1, "pcs", "2026-11-17", false, false, 7],
  ["Oats", 340, "g", "2026-11-30", false, false, 8],
  ["Rice", 1000, "g", "2026-12-20", false, false, 9],
  ["Pasta", 3, "pcs", "2027-02-18", false, false, 10],
  ["Ketchup", 250, "ml", null, false, false, 11],
  ["Soup", 1, "pcs", null, false, false, 12],
  ["Old Soup", 1, "pcs", "2026-11-20", true, false, 13],
  ["Wrench", 1, "pcs", null, false, true, 14],
];

const made = {};
for (const [name, qty, unit, expiry, gone, unsorted, hue] of items) {
  const eid = await evidence(hue);
  const asset = await call("POST", `/v1/assets?${H}`, {
    display_name: name,
    asset_type: "product",
    quantity: qty,
    unit: unit || null,
    evidence_ids: [eid],
  });
  made[name] = asset.id;
  if (!unsorted) {
    await call("POST", `/v1/plugins/expiry-tracker/assets/${asset.id}/classification?${H}`, { category: "food_beverages" });
  }
  if (expiry) {
    await call("POST", `/v1/plugins/expiry-tracker/assets/${asset.id}/expiry?${H}`, {
      expiry_date: expiry,
      date_type: "expiry_date",
    });
  }
  if (gone) await call("POST", `/v1/assets/${asset.id}/gone?${H}`, { reason: "used_up" });
  console.log("made", name, asset.id);
}
console.log(JSON.stringify(made));
