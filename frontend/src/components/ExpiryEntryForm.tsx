import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { clearExpiryDate, enterManualExpiry } from "../api/client";
import type { Assertion } from "../api/types";

export const DATE_TYPE_LABELS: Record<string, string> = {
  expiry_date: "Expiry date",
  best_before: "Best before",
  use_by: "Use by",
  manufacture_date: "Manufacture date",
  period_after_opening: "Period after opening",
  batch_lot_code: "Batch/lot code",
  valid_until: "Valid until",
};

function valueRecord(value: unknown): Record<string, unknown> | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  return value as Record<string, unknown>;
}

export function ExpiryEntryForm({
  assetId,
  householdId,
  evidenceIds = [],
  activeAssertion = null,
  categorySlug = "",
  hasWindows = true,
}: {
  assetId: string;
  householdId: string;
  evidenceIds?: string[];
  activeAssertion?: Assertion | null;
  categorySlug?: string;
  hasWindows?: boolean;
}) {
  const qc = useQueryClient();
  const record = valueRecord(activeAssertion?.value);
  const documents = categorySlug === "documents_other";
  const defaultDateType = documents ? "valid_until" : "expiry_date";
  const [date, setDate] = useState(
    typeof record?.expiry_date === "string" ? record.expiry_date : ""
  );
  const [dateType, setDateType] = useState(
    typeof record?.date_type === "string" ? record.date_type : defaultDateType
  );
  const [submitting, setSubmitting] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!hasWindows) return null;

  const state = activeAssertion?.review_state || "needs_evidence";
  const activeDate = typeof record?.expiry_date === "string" ? record.expiry_date : null;
  const activeDateType = typeof record?.date_type === "string" ? record.date_type : null;
  const noOp =
    activeAssertion?.review_state === "accepted" &&
    activeDate !== null &&
    activeDateType !== null &&
    date === activeDate &&
    dateType === activeDateType;
  const isBtnDisabled = submitting || clearing || !date || noOp;
  const title = documents ? "Manual date entry" : "Manual expiry entry";
  const dateTypes = documents
    ? ["valid_until", ...Object.keys(DATE_TYPE_LABELS).filter((item) => item !== "valid_until")]
    : Object.keys(DATE_TYPE_LABELS);

  async function submit() {
    if (submitting || !date) return;
    setSubmitting(true);
    setError(null);
    setMessage(null);
    try {
      await enterManualExpiry(
        assetId,
        householdId,
        { expiry_date: date, date_type: dateType, source_evidence_ids: evidenceIds },
        activeAssertion?.id
      );
      await qc.invalidateQueries({ queryKey: ["asset", assetId, householdId] });
      setMessage("Date saved and re-read from the asset.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setSubmitting(false);
    }
  }

  async function clear() {
    if (clearing) return;
    setClearing(true);
    setError(null);
    setMessage(null);
    try {
      await clearExpiryDate(assetId, householdId, activeAssertion?.id);
      await qc.invalidateQueries({ queryKey: ["asset", assetId, householdId] });
      setDate("");
      setMessage("Date cleared.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setClearing(false);
    }
  }

  return (
    <section aria-label={title} className="bg-card border-border" style={{ marginTop: 18, padding: 14, borderStyle: "solid", borderWidth: 1, borderRadius: 8 }}>
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      <div>Expiry evidence state: <strong data-testid="expiry-state">{state}</strong></div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10, alignItems: "end" }}>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 13 }}>
          Date
          <input
            type="date"
            value={date}
            onChange={(event) => setDate(event.target.value)}
            className="bg-background text-foreground border-border focus-ring"
            style={{ padding: "6px 10px", borderRadius: 6, borderStyle: "solid", borderWidth: 1 }}
          />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 13 }}>
          Date type
          <select
            value={dateType}
            onChange={(event) => setDateType(event.target.value)}
            className="bg-background text-foreground border-border focus-ring"
            style={{ padding: "6px 10px", borderRadius: 6, borderStyle: "solid", borderWidth: 1 }}
          >
            {dateTypes.map((item) => (
              <option key={item} value={item}>{DATE_TYPE_LABELS[item] ?? item}</option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={submit}
          disabled={isBtnDisabled}
          title={!date ? "Select a date to save" : undefined}
          className="bg-primary text-primary-foreground focus-ring"
          style={{
            padding: "6px 12px",
            borderRadius: 6,
            border: "none",
            cursor: isBtnDisabled ? "not-allowed" : "pointer",
            fontWeight: 500,
          }}
        >
          {submitting ? "Saving…" : state === "proposed" ? "Accept date" : "Save date"}
        </button>
        {activeDate !== null && (
          <button
            type="button"
            onClick={clear}
            disabled={clearing || submitting}
            className="bg-card text-foreground border-border focus-ring"
            style={{ padding: "6px 12px", borderRadius: 6, borderStyle: "solid", borderWidth: 1, cursor: "pointer" }}
          >
            {documents ? "Clear date" : "Clear expiry date"}
          </button>
        )}
      </div>
      {message && <div role="status" className="text-success" style={{ marginTop: 8 }}>{message}</div>}
      {error && <div role="alert" className="text-danger" style={{ marginTop: 8 }}>{error}</div>}
    </section>
  );
}
