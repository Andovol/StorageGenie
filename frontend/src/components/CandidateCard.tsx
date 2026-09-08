import { useMemo, useState } from "react";
import type { Candidate, CandidateField, DedupMatch } from "../api/types";

function fieldInfo(raw: CandidateField) {
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    const value = (raw as Record<string, unknown>).value;
    return {
      value,
      confidence: (raw as Record<string, unknown>).confidence,
      source: (raw as Record<string, unknown>).source_type ?? (raw as Record<string, unknown>).source ?? "deterministic",
    };
  }
  return { value: raw, confidence: null, source: "deterministic" };
}

function matchLabel(match: DedupMatch) {
  if (match.type === "identifier_collision") return `Identifier collision: ${match.identifier || "unknown identifier"}`;
  if (match.type === "duplicate_of_asset") return `Exact duplicate of asset ${match.asset_id || "unknown"}`;
  if (match.type === "similar") return `Similar to asset ${match.asset_id || "unknown"}${match.distance != null ? ` (distance ${match.distance})` : ""}`;
  return match.type;
}

export function CandidateCard({
  candidate,
  householdId,
  onDecision,
  busy = false,
}: {
  candidate: Candidate;
  householdId: string;
  onDecision: (action: "accept" | "edit" | "hold" | "reject", correctedFields?: Record<string, unknown>) => void;
  busy?: boolean;
}) {
  const [values, setValues] = useState<Record<string, unknown>>(() => {
    const initial: Record<string, unknown> = {};
    Object.entries(candidate.fields).forEach(([key, raw]) => { initial[key] = fieldInfo(raw).value ?? ""; });
    return initial;
  });
  const blocked = candidate.review_task_ids.length > 0;
  const evidenceUrls = useMemo(() => {
    const base = import.meta.env.VITE_API_BASE || "http://localhost:8000";
    return candidate.evidence_ids.map((id) => ({ id, url: `${base}/v1/evidence/${id}/thumb/256?household_id=${householdId}` }));
  }, [candidate.evidence_ids, householdId]);

  return (
    <article style={{ border: "1px solid #e5e7eb", borderRadius: 10, padding: 16, background: "white" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12 }}>
        <div><h2 style={{ margin: 0 }}>Candidate {candidate.id}</h2><div style={{ color: "#6b7280", fontSize: 12 }}>State: {candidate.state} · Job: {candidate.job_id}</div></div>
        <span>Candidate review</span>
      </div>
      {candidate.dedup_matches.length > 0 && (
        <div role="alert" style={{ marginTop: 14, padding: 10, background: "#fff7ed", border: "1px solid #fed7aa", borderRadius: 6 }}>
          <strong>Possible duplicates or collisions</strong>
          {candidate.dedup_matches.map((match, index) => <div key={`${match.type}-${index}`}>{matchLabel(match)}</div>)}
          {blocked ? <div style={{ marginTop: 4 }}>Acceptance is blocked until the open review task(s) are resolved.</div> : <div style={{ marginTop: 4 }}>This match is advisory; review it before accepting.</div>}
        </div>
      )}
      <div style={{ display: "grid", gridTemplateColumns: "minmax(180px, 1fr) minmax(240px, 1.2fr)", gap: 20, marginTop: 18 }}>
        <section aria-label="Candidate fields">
          <h3 style={{ marginTop: 0 }}>Candidate fields</h3>
          {Object.entries(candidate.fields).map(([key, raw]) => {
            const info = fieldInfo(raw);
            return <div key={key} style={{ padding: "8px 0", borderBottom: "1px solid #f3f4f6" }}>
              <label htmlFor={`candidate-field-${key}`} style={{ display: "block", fontWeight: 600 }}>{key}</label>
              <input id={`candidate-field-${key}`} aria-label={`${key} value`} value={String(values[key] ?? "")} placeholder="Unknown" onChange={(event) => setValues((previous) => ({ ...previous, [key]: event.target.value }))} style={{ width: "100%", boxSizing: "border-box", padding: 7, marginTop: 4, border: "1px solid #d1d5db", borderRadius: 5 }} />
              <div style={{ fontSize: 11, color: "#6b7280", marginTop: 3 }}>Confidence: {info.confidence == null ? "Unknown" : String(info.confidence)} · Source: {String(info.source)}</div>
            </div>;
          })}
          {Object.keys(candidate.fields).length === 0 && <div>Unknown</div>}
        </section>
        <section aria-label="Source evidence">
          <h3 style={{ marginTop: 0 }}>Source evidence</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
            {evidenceUrls.map((evidence) => <figure key={evidence.id} style={{ margin: 0 }}><img src={evidence.url} alt={`Evidence ${evidence.id}`} style={{ width: 160, height: 120, objectFit: "contain", background: "#f3f4f6" }} /><figcaption style={{ fontSize: 11, color: "#6b7280" }}>{evidence.id}</figcaption></figure>)}
          </div>
          {evidenceUrls.length === 0 && <div>No source evidence</div>}
        </section>
      </div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 18 }}>
        <button type="button" onClick={() => onDecision("accept", values)} disabled={busy || blocked}>Accept</button>
        <button type="button" onClick={() => onDecision("edit", values)} disabled={busy}>Save edits</button>
        <button type="button" onClick={() => onDecision("hold")} disabled={busy}>Hold / Unknown</button>
        <button type="button" onClick={() => onDecision("reject")} disabled={busy}>Reject</button>
      </div>
    </article>
  );
}
