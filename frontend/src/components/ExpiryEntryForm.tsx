import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet, enterManualExpiry } from "../api/client";
import type { Asset } from "../api/types";

export function ExpiryEntryForm({ assetId, householdId, evidenceIds = [] }: { assetId: string; householdId: string; evidenceIds?: string[] }) {
  const qc = useQueryClient();
  const [date, setDate] = useState("");
  const [dateType, setDateType] = useState("expiry_date");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const assetQuery = useQuery<Asset>({
    queryKey: ["asset", assetId, householdId],
    queryFn: () => apiGet<Asset>(`/v1/assets/${assetId}`, { household_id: householdId }),
    enabled: !!assetId && !!householdId,
  });
  const expiry = assetQuery.data?.assertions?.find((assertion) => assertion.field_path.endsWith("expiry_date"));
  const state = expiry?.review_state || "needs_evidence";

  async function submit() {
    if (submitting || !date) return;
    setSubmitting(true);
    setError(null);
    setMessage(null);
    try {
      await enterManualExpiry(assetId, householdId, { expiry_date: date, date_type: dateType, source_evidence_ids: evidenceIds });
      await qc.invalidateQueries({ queryKey: ["asset", assetId, householdId] });
      setMessage("Expiry saved and re-read from the asset.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setSubmitting(false);
    }
  }

  const isBtnDisabled = assetQuery.isLoading || submitting || !date;

  return (
    <section aria-label="Manual expiry entry" className="bg-card border-border" style={{ marginTop: 18, padding: 14, borderStyle: "solid", borderWidth: 1, borderRadius: 8 }}>
      <h3 style={{ marginTop: 0 }}>Manual expiry entry</h3>
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
            <option value="expiry_date">Expiry date</option>
            <option value="best_before">Best before</option>
            <option value="use_by">Use by</option>
            <option value="manufacture_date">Manufacture date</option>
            <option value="period_after_opening">Period after opening</option>
            <option value="batch_lot_code">Batch/lot code</option>
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
          {submitting ? "Saving…" : "Save expiry"}
        </button>
      </div>
      {message && <div role="status" className="text-success" style={{ marginTop: 8 }}>{message}</div>}
      {error && <div role="alert" className="text-danger" style={{ marginTop: 8 }}>{error}</div>}
    </section>
  );
}
