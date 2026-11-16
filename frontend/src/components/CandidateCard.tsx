import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import type { Candidate, CandidateField, DedupMatch } from "../api/types";
import {
  ASSET_TYPE_LABELS,
  CANDIDATE_STATE_LABELS,
  PRODUCT_STATUS_LABELS,
  STEP_STATE_LABELS,
  formatUseByDate,
} from "../lib/labels";
import { WebAlternates } from "./WebAlternates";
import { CONTROL_STYLE, THEMED_CONTROL_CLASS } from "./shell/CatalogToolbar";

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

/** SG-304 G2: the existing item a duplicate photo matches, by name and date. */
export type DuplicateOf = { name: string; expiry: string | null };

/** SG-304 G2: "This photo matches Olive Oil (use by 10 Jan 2027)." Never an id. */
function duplicateLine(duplicateOf: DuplicateOf | null): string {
  if (!duplicateOf || !duplicateOf.name) return "This photo matches an item you already have.";
  const when = duplicateOf.expiry ? ` (use by ${formatUseByDate(duplicateOf.expiry)})` : " (no date set)";
  return `This photo matches ${duplicateOf.name}${when}.`;
}

function matchLabel(match: DedupMatch) {
  if (match.type === "identifier_collision") return `Identifier collision: ${match.identifier || "unknown identifier"}`;
  if (match.type === "similar") return `Similar to asset ${match.asset_id || "unknown"}${match.distance != null ? ` (distance ${match.distance})` : ""}`;
  return match.type;
}

// SG-271 G4: one name per concept. The capture kind and the AI's shelf-life
// suggestion never both read as "category".
// SG-325 P12: every key the API's candidate shape carries reads as plain
// words — Name, Use by, Status, Identifier, Brand — never raw. Unknown keys
// are title-cased, never raw; a trailing expiry_date (e.g. the plugin's
// `plugin:expiry-tracker/expiry_date`) still reads Use by.
const FIELD_LABELS: Record<string, string> = {
  display_name: "Name",
  expiry_date: "Use by",
  status: "Status",
  identifier: "Identifier",
  brand: "Brand",
  asset_type: "Kind of item",
  category_proposed: "Suggested shelf life",
};

function plainFieldLabel(key: string): string {
  if (FIELD_LABELS[key]) return FIELD_LABELS[key];
  if (key.endsWith("expiry_date")) return "Use by";
  return key.replace(/[_.:]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * SG-325 P12: a source word shows its labels.ts plain word when one exists;
 * otherwise the raw word stays. Checked maps: STEP_STATE_LABELS,
 * CANDIDATE_STATE_LABELS, ASSET_TYPE_LABELS, PRODUCT_STATUS_LABELS
 * (EXPIRY_STATE_LABELS is not exported). Observed raw words with no entry
 * (left as-is): ocr, user, extraction, deterministic.
 */
function labelSourceWord(source: unknown): string {
  const raw = String(source ?? "");
  if (STEP_STATE_LABELS[raw.toUpperCase()]) return STEP_STATE_LABELS[raw.toUpperCase()];
  if (CANDIDATE_STATE_LABELS[raw]) return CANDIDATE_STATE_LABELS[raw];
  if (ASSET_TYPE_LABELS[raw]) return ASSET_TYPE_LABELS[raw];
  if (PRODUCT_STATUS_LABELS[raw]) return PRODUCT_STATUS_LABELS[raw];
  return raw;
}

export function CandidateCard({
  candidate,
  householdId,
  onDecision,
  busy = false,
  splitItemCount = null,
  onSplit,
  splitBusy = false,
  duplicateOf = null,
}: {
  candidate: Candidate;
  householdId: string;
  onDecision: (
    action: "accept" | "edit" | "hold" | "reject",
    correctedFields?: Record<string, unknown>,
    options?: { asNewPack?: boolean }
  ) => void;
  busy?: boolean;
  splitItemCount?: number | null;
  onSplit?: () => void;
  splitBusy?: boolean;
  duplicateOf?: DuplicateOf | null;
}) {
  const [values, setValues] = useState<Record<string, unknown>>(() => {
    const initial: Record<string, unknown> = {};
    Object.entries(candidate.fields).forEach(([key, raw]) => { initial[key] = fieldInfo(raw).value ?? ""; });
    return initial;
  });
  const blockingTaskIds = candidate.blocking_review_task_ids;
  const blocked = blockingTaskIds.length > 0;
  // SG-304 G2: on a duplicate photo the three choices replace Accept and Hold.
  const firstDuplicateIndex = candidate.dedup_matches.findIndex((match) => match.type === "duplicate_of_asset");
  const isDuplicate = firstDuplicateIndex >= 0;
  const dateOnly = !blocked && candidate.review_task_ids.length > 0;
  const evidenceUrls = useMemo(() => {
    const base = import.meta.env.VITE_API_BASE || "http://localhost:8003";
    return candidate.evidence_ids.map((id) => ({ id, url: `${base}/v1/evidence/${id}/thumb/256?household_id=${householdId}` }));
  }, [candidate.evidence_ids, householdId]);
  const [failedEvidenceIds, setFailedEvidenceIds] = useState<Set<string>>(new Set());

  return (
    <article className="bg-card border-border" style={{ borderStyle: "solid", borderWidth: 1, borderRadius: 10, padding: 16 }}>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "baseline", gap: 12 }}>
        <div><h2 style={{ margin: 0 }}>Check this item</h2></div>
      </div>
      {candidate.dedup_matches.length > 0 && (
        <div role="alert" className="bg-accent border-accent" style={{ marginTop: 14, padding: 10, borderStyle: "solid", borderWidth: 1, borderRadius: 6 }}>
          <strong>This may already be in your catalog</strong>
          {candidate.dedup_matches.map((match, index) => match.type === "duplicate_of_asset"
            ? (index === firstDuplicateIndex ? <div key={`${match.type}-${index}`}>{duplicateLine(duplicateOf)}</div> : null)
            : <div key={`${match.type}-${index}`}>{matchLabel(match)}</div>)}
          {isDuplicate && (
            <div role="group" aria-label="Duplicate choices" style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 8 }}>
              <button type="button" onClick={() => onDecision("accept", values, { asNewPack: true })} disabled={busy || blocked} className="bg-primary text-primary-foreground focus-ring" style={{ ...CONTROL_STYLE, border: "none", opacity: busy || blocked ? 0.5 : 1, cursor: busy || blocked ? "not-allowed" : "pointer" }}>
                {"It's another pack"}
              </button>
              <button type="button" onClick={() => onDecision("accept", values)} disabled={busy || blocked} className={THEMED_CONTROL_CLASS} style={{ ...CONTROL_STYLE, opacity: busy || blocked ? 0.5 : 1, cursor: busy || blocked ? "not-allowed" : "pointer" }}>
                {"It's the same pack"}
              </button>
              <button type="button" onClick={() => onDecision("hold")} disabled={busy} className={THEMED_CONTROL_CLASS} style={{ ...CONTROL_STYLE, opacity: busy ? 0.5 : 1, cursor: busy ? "not-allowed" : "pointer" }}>
                Decide later
              </button>
            </div>
          )}
        </div>
      )}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(240px, 100%), 1fr))", gap: 20, marginTop: 18 }}>
        <section aria-label="What we read">
          <h3 style={{ marginTop: 0 }}>What we read</h3>
          {Object.entries(candidate.fields).map(([key, raw]) => {
            const info = fieldInfo(raw);
            const label = plainFieldLabel(key);
            const isUseBy = key === "expiry_date" || key.endsWith("expiry_date");
            return <div key={key} className="border-border" style={{ padding: "8px 0", borderBottomStyle: "solid", borderBottomWidth: 1 }}>
              <label htmlFor={`candidate-field-${key}`} style={{ display: "block", fontWeight: 600 }}>{label}</label>
              <input id={`candidate-field-${key}`} aria-label={label} type={isUseBy ? "date" : undefined} value={String(values[key] ?? "")} placeholder="Unknown" onChange={(event) => setValues((previous) => ({ ...previous, [key]: event.target.value }))} className="bg-background text-foreground border-border focus-ring" style={{ width: "100%", boxSizing: "border-box", padding: 7, marginTop: 4, borderStyle: "solid", borderWidth: 1, borderRadius: 5 }} />
              <div className="text-muted-foreground" style={{ fontSize: 13, marginTop: 3 }}>Confidence: {info.confidence == null ? "Unknown" : String(info.confidence)} · Source: {labelSourceWord(info.source)}</div>
            </div>;
          })}
          {Object.keys(candidate.fields).length === 0 && <div>Unknown</div>}
        </section>
        <section aria-label="Photo">
          <h3 style={{ marginTop: 0 }}>Photo</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
            {evidenceUrls.map((evidence) => <figure key={evidence.id} style={{ margin: 0 }}>{failedEvidenceIds.has(evidence.id) ? <div tabIndex={0} className="bg-card-muted text-muted-foreground focus-ring" style={{ width: 160, height: 120, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, padding: 4, textAlign: "center" }}>No photo yet</div> : <img src={evidence.url} alt={`Evidence ${evidence.id}`} className="bg-card-muted" style={{ width: 160, height: 120, objectFit: "contain" }} onError={() => setFailedEvidenceIds((previous) => new Set(previous).add(evidence.id))} />}</figure>)}
          </div>
          {evidenceUrls.length === 0 && <div>No source evidence</div>}
        </section>
      </div>
      <WebAlternates alternates={candidate.web_alternates ?? []} />
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 18 }}>
        {!isDuplicate && (
        <span title={blocked ? "Acceptance is blocked until open review tasks are resolved" : undefined}>
          <button
            type="button"
            onClick={() => onDecision("accept", values)}
            disabled={busy || blocked}
            className="bg-primary text-primary-foreground focus-ring"
            style={{ ...CONTROL_STYLE, border: "none", opacity: busy || blocked ? 0.5 : 1, cursor: busy || blocked ? "not-allowed" : "pointer" }}
          >
            Accept
          </button>
        </span>
        )}
        {!isDuplicate && (
        <button
          type="button"
          onClick={() => onDecision("edit", values)}
          disabled={busy}
          className={`${THEMED_CONTROL_CLASS}`}
          style={{ ...CONTROL_STYLE, opacity: busy ? 0.5 : 1, cursor: busy ? "not-allowed" : "pointer" }}
        >
          Save edits
        </button>
        )}
        {!isDuplicate && (
        <button
          type="button"
          onClick={() => onDecision("hold")}
          disabled={busy}
          className={`${THEMED_CONTROL_CLASS}`}
          style={{ ...CONTROL_STYLE, opacity: busy ? 0.5 : 1, cursor: busy ? "not-allowed" : "pointer" }}
        >
          Hold / Unknown
        </button>
        )}
        <button
          type="button"
          onClick={() => onDecision("reject")}
          disabled={busy}
          className={`${THEMED_CONTROL_CLASS}`}
          style={{ ...CONTROL_STYLE, opacity: busy ? 0.5 : 1, cursor: busy ? "not-allowed" : "pointer" }}
        >
          Reject
        </button>
        {splitItemCount != null && onSplit && (
          <button
            type="button"
            onClick={onSplit}
            disabled={busy || splitBusy}
            className={`${THEMED_CONTROL_CLASS}`}
            style={{ ...CONTROL_STYLE, opacity: busy || splitBusy ? 0.5 : 1, cursor: busy || splitBusy ? "not-allowed" : "pointer" }}
          >
            Split into {splitItemCount} items
          </button>
        )}
      </div>
      {blocked && (
        <p style={{ marginTop: 10, marginBottom: 0 }}>
          Acceptance is blocked until the open review task(s) are resolved.{" "}
          <Link to={`/inbox?household_id=${householdId}`} className="text-link focus-ring">View them in the Inbox.</Link>
        </p>
      )}
      {dateOnly && (
        <p style={{ marginTop: 10, marginBottom: 0 }}>The date can be added after accepting.</p>
      )}
    </article>
  );
}
