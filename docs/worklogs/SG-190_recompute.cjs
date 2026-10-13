#!/usr/bin/env node
// SG-190 recompute/verify — reads the raw driver result JSONs (candidate first, base second)
// and recomputes every number this slice claims. No browser, no network, offline only.
// Exit 0 only if the candidate checks pass; base numbers are printed for comparison and may
// legitimately fail them (that is the point of the comparison).
//
// Usage: node SG-190_recompute.cjs <candidate_result.json> [base_result.json]

const fs = require("fs");

function load(p) { return JSON.parse(fs.readFileSync(p, "utf8")); }

function overflowSummary(app) {
  const by = {};
  for (const r of app.routes.filter((r) => r.measured)) {
    by[r.viewport] ??= { routes: 0, overflow: 0, offenders: 0 };
    by[r.viewport].routes++;
    if (r.measure.docOverflowX > 0) by[r.viewport].overflow++;
    by[r.viewport].offenders += (r.measure.offenders || []).length;
  }
  return by;
}

function contrastSummary(app) {
  let below = 0, min = Infinity, minSample = null, samples = 0, unknown = 0;
  const byPair = {};
  for (const r of app.routes.filter((r) => r.measured && r.measure.contrast)) {
    for (const c of r.measure.contrast) {
      samples++;
      if (c.ratio_exact == null) { unknown++; continue; }
      if (c.passesAA === false) below++;
      if (c.ratio_exact < min) {
        min = c.ratio_exact;
        minSample = { route: r.route, viewport: r.viewport, text: c.text, fg: c.fg_computed, bg: JSON.stringify(c.bg_effective), ratio: c.ratio_exact };
      }
      const key = c.fg_computed + " on " + JSON.stringify(c.bg_effective.b) ;
      byPair[key] ??= { count: 0, min: Infinity };
      byPair[key].count++;
      if (c.ratio_exact < byPair[key].min) byPair[key].min = c.ratio_exact;
    }
  }
  const top = Object.entries(byPair).sort((a, b) => b[1].count - a[1].count).slice(0, 6).map(([k, v]) => ({ pair: k, count: v.count, min: v.min }));
  return { samples, below, unknown, min, minSample, topPairs: top };
}

function targetSummary(app) {
  const t = {};
  for (const r of app.routes.filter((r) => r.targetDispositions)) for (const d of r.targetDispositions) t[d.disposition] = (t[d.disposition] || 0) + 1;
  return t;
}

function check(candidate) {
  const app = candidate.app;
  const ov = overflowSummary(app);
  const con = contrastSummary(app);
  const targets = targetSummary(app);
  const tab = app.tabProbes && app.tabProbes[0];
  const closed = (app.menuProbes || []).filter((m) => m.phase === "closed" && m.viewport === "390x844");
  const open = (app.menuProbes || []).find((m) => m.phase === "open-clicked");
  const wide = (app.menuProbes || []).find((m) => m.phase === "toggle-hidden-1440");
  const checks = {
    overflow_zero_all_viewports: ["390x844", "834x1112", "1440x900", "320x720"].every((v) => ov[v] && ov[v].overflow === 0),
    contrast_no_below_AA: con.below === 0,
    controls_all_pass: !!candidate.controls && candidate.controls.controls.every((c) => c.ok),
    transport_get_only: app.guardAggregate && Object.keys(app.guardAggregate.methods).every((m) => m === "GET" || m === "HEAD" || m === "OPTIONS") && app.guardAggregate.blockedExternal.length === 0,
    tab_probe_clean: !!tab && tab.obscuredCount === 0 && tab.invisibleCount === 0,
    menu_closed_no_visible_links: closed.length === 10 && closed.every((m) => m.menuDisplay === "none" && m.links.filter((l) => l.visibleInViewport).length === 0),
    menu_open_all_links_visible: !!open && open.menuDisplay === "flex" && open.links.length === 8 && open.links.every((l) => l.visibleInViewport),
    menu_toggle_hidden_wide: !!wide && wide.toggleDisplay === "none" && wide.menuDisplay === "flex",
    draft_preserved: !!app.draftProbe && app.draftProbe.preserved === true,
  };
  return { ov, con, targets, tab, checks };
}

function main() {
  const [candidatePath, basePath] = process.argv.slice(2);
  if (!candidatePath) { console.error("usage: node SG-190_recompute.cjs <candidate.json> [base.json]"); process.exit(2); }
  const candidate = load(candidatePath);
  const result = { candidate: check(candidate) };

  console.log("== candidate ==");
  console.log("browser:", candidate.browser["Browser"] || candidate.browser.versionProtocol);
  console.log("serve:", JSON.stringify(candidate.serve));
  console.log("overflow by viewport:", JSON.stringify(result.candidate.ov));
  console.log("contrast: samples=" + result.candidate.con.samples + " belowAA=" + result.candidate.con.below + " unknown=" + result.candidate.con.unknown + " min=" + result.candidate.con.min);
  console.log("contrast min sample:", JSON.stringify(result.candidate.con.minSample));
  console.log("contrast top pairs:", JSON.stringify(result.candidate.con.topPairs));
  console.log("target dispositions:", JSON.stringify(result.candidate.targets));
  console.log("controls:", JSON.stringify(candidate.controls.controls.map((c) => ({ [c.name]: c.ok }))));
  console.log("tab probe:", result.candidate.tab ? JSON.stringify({ tabs: result.candidate.tab.tabs, obscured: result.candidate.tab.obscuredCount, invisible: result.candidate.tab.invisibleCount }) : "none");
  console.log("draft probe:", JSON.stringify(candidate.app.draftProbe));
  console.log("guard:", JSON.stringify(candidate.app.guardAggregate.methods), "blocked=" + candidate.app.guardAggregate.blocked.length, "externalBlocked=" + candidate.app.guardAggregate.blockedExternal.length, "fulfilled=" + candidate.app.guardAggregate.fulfilledFromLoopback, "fulfillFailures=" + candidate.app.guardAggregate.fulfillFailures);
  console.log("checks:", JSON.stringify(result.candidate.checks));

  if (basePath) {
    const base = load(basePath);
    result.base = check(base);
    console.log("== base ==");
    console.log("overflow by viewport:", JSON.stringify(result.base.ov));
    console.log("contrast: samples=" + result.base.con.samples + " belowAA=" + result.base.con.below + " min=" + result.base.con.min);
    console.log("contrast min sample:", JSON.stringify(result.base.con.minSample));
    console.log("target dispositions:", JSON.stringify(result.base.targets));
    console.log("base checks (expected to fail):", JSON.stringify(result.base.checks));
  }

  const ok = Object.values(result.candidate.checks).every(Boolean);
  console.log("RESULT " + JSON.stringify({ ok, checks: result.candidate.checks }));
  process.exit(ok ? 0 : 1);
}

main();
