import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet, enterManualExpiry } from "../api/client";
import type { Asset } from "../api/types";

export function ExpiryEntryForm({ assetId, householdId, evidenceIds = [] }: { assetId: string; householdId: string; evidenceIds?: string[] }) {
  const qc = useQueryClient();
  const [date, setDate] = useState("");
  const [dateType, setDateType] = useState("expiry_date");
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
    setError(null); setMessage(null);
    try {
      await enterManualExpiry(assetId, householdId, { expiry_date: date, date_type: dateType, source_evidence_ids: evidenceIds });
      await qc.invalidateQueries({ queryKey: ["asset", assetId, householdId] });
      setMessage("Expiry saved and re-read from the asset.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    }
  }

  return (
    <section aria-label="Manual expiry entry" style={{ marginTop: 18, padding: 14, border: "1px solid #e5e7eb", borderRadius: 8 }}>
      <h3 style={{ marginTop: 0 }}>Manual expiry entry</h3>
      <div>Expiry evidence state: <strong data-testid="expiry-state">{state}</strong></div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10, alignItems: "end" }}>
        <label>Date<input type="date" value={date} onChange={(event) => setDate(event.target.value)} style={{ display: "block", padding: 7 }} /></label>
        <label>Date type<select value={dateType} onChange={(event) => setDateType(event.target.value)} style={{ display: "block", padding: 7 }}><option value="expiry_date">Expiry date</option><option value="best_before">Best before</option><option value="use_by">Use by</option><option value="manufacture_date">Manufacture date</option><option value="period_after_opening">Period after opening</option><option value="batch_lot_code">Batch/lot code</option></select></label>
        <button type="button" onClick={submit} disabled={assetQuery.isLoading || !date}>Save expiry</button>
      </div>
      {message && <div role="status" style={{ color: "#166534", marginTop: 8 }}>{message}</div>}
      {error && <div role="alert" style={{ color: "#b91c1c", marginTop: 8 }}>{error}</div>}
    </section>
  );
}
