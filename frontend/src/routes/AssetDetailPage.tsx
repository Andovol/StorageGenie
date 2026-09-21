import { useState } from "react";
import { useParams, useSearchParams, Link } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useAsset } from "../hooks/useAssets";
import { EvidenceGallery } from "../components/EvidenceGallery";
import { ProvenanceBadge } from "../components/ProvenanceBadge";
import { ExpiryEntryForm } from "../components/ExpiryEntryForm";
import { apiPatch, apiPost, uploadEvidence } from "../api/client";
import { UNTITLED_ASSET_NAME } from "../types/product";

export function AssetDetailPage() {
  const { id } = useParams();
  const [search] = useSearchParams();
  const householdId = search.get("household_id") || localStorage.getItem("household_id") || "";
  const { data: asset, isLoading } = useAsset(householdId, id || "");
  const qc = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editQuantity, setEditQuantity] = useState("");
  const [editUnit, setEditUnit] = useState("");
  const [editCondition, setEditCondition] = useState("");
  const [attachFiles, setAttachFiles] = useState<FileList | null>(null);
  const [error, setError] = useState<string | null>(null);

  const patchMut = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      apiPatch(`/v1/assets/${id}`, payload, { household_id: householdId }, { "If-Match": String(asset?.version ?? 1) }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["asset", id] });
      setEditing(false);
    },
    onError: (e: unknown) => setError(e instanceof Error ? e.message : String(e)),
  });

  const attachMut = useMutation({
    mutationFn: async () => {
      if (!attachFiles?.length || !id) throw new Error("No files selected");
      const ids: string[] = [];
      for (const f of Array.from(attachFiles)) {
        const ev = await uploadEvidence(householdId, f);
        ids.push(ev.id);
      }
      return apiPost(`/v1/assets/${id}/evidence`, { evidence_ids: ids }, { household_id: householdId });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["asset", id] });
      setAttachFiles(null);
      (document.getElementById("attach-input") as HTMLInputElement | null)?.value &&
        ((document.getElementById("attach-input") as HTMLInputElement).value = "");
    },
    onError: (e: unknown) => setError(e instanceof Error ? e.message : String(e)),
  });

  if (isLoading) return <div style={{ padding: 24 }}>Loading...</div>;
  if (!asset) return <div style={{ padding: 24 }}>Asset not found — <Link to="/">back to catalog</Link></div>;

  const evidence = (asset as unknown as { evidence: { id: string; storage_key: string; sha256: string; original_filename: string }[] }).evidence || [];
  const assertions = asset.assertions || [];
  const expiryAssertion = assertions.find((item) => item.field_path.endsWith("expiry_date"));
  const audits = (asset as unknown as { audit_events: { id: string; action: string; actor: string; timestamp: string; before: unknown; after: unknown }[] }).audit_events || [];
  const displayName = asset.display_name || UNTITLED_ASSET_NAME;

  return (
    <div className="text-foreground" style={{ padding: 24, maxWidth: 900 }}>
      <Link to={`/?household_id=${householdId}`} className="text-primary focus-ring" style={{ fontSize: 13 }}>← Back to catalog</Link>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 8 }}>
        <h1 className="page-header text-foreground" style={{ margin: 0 }}>{displayName}</h1>
        <button
          onClick={() => {
            setEditName(asset.display_name ?? "");
            setEditQuantity(asset.quantity != null ? String(asset.quantity) : "");
            setEditUnit(asset.unit ?? "");
            setEditCondition(asset.condition ?? "");
            setEditing((v) => !v);
          }}
          className="bg-card text-foreground border-border focus-ring"
          style={{ padding: "6px 12px", borderRadius: 6, borderStyle: "solid", borderWidth: 1, cursor: "pointer" }}
        >
          {editing ? "Cancel" : "Edit"}
        </button>
      </div>
      <div className="text-muted-foreground" style={{ marginBottom: 12, fontSize: 13 }}>
        {asset.asset_type} · {asset.status} · v{asset.version} · {asset.household_id.slice(0, 8)}
        {asset.quantity != null && <> · qty {asset.quantity} {asset.unit || ""}</>}
        {asset.condition && <> · {asset.condition}</>}
      </div>

      {editing && (
        <div className="bg-card-muted border-border" style={{ borderRadius: 8, padding: 12, marginBottom: 16, borderStyle: "solid", borderWidth: 1 }}>
          <div style={{ display: "grid", gridTemplateColumns: "110px 1fr", gap: 8, alignItems: "center" }}>
            <label htmlFor="edit-display-name" style={{ fontSize: 13 }}>Display name</label>
            <input id="edit-display-name" value={editName} onChange={(e) => setEditName(e.target.value)} className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderRadius: 6, borderStyle: "solid", borderWidth: 1 }} />
            <label htmlFor="edit-quantity" style={{ fontSize: 13 }}>Quantity</label>
            <input id="edit-quantity" type="number" value={editQuantity} onChange={(e) => setEditQuantity(e.target.value)} className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderRadius: 6, borderStyle: "solid", borderWidth: 1 }} />
            <label htmlFor="edit-unit" style={{ fontSize: 13 }}>Unit</label>
            <input id="edit-unit" value={editUnit} onChange={(e) => setEditUnit(e.target.value)} className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderRadius: 6, borderStyle: "solid", borderWidth: 1 }} />
            <label htmlFor="edit-condition" style={{ fontSize: 13 }}>Condition</label>
            <input id="edit-condition" value={editCondition} onChange={(e) => setEditCondition(e.target.value)} className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderRadius: 6, borderStyle: "solid", borderWidth: 1 }} />
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 10 }}>
            <button
              onClick={() => {
                const payload: Record<string, unknown> = { display_name: editName.trim() };
                if (editQuantity.trim() !== "") payload.quantity = Number(editQuantity);
                if (editUnit.trim() !== "") payload.unit = editUnit.trim();
                if (editCondition.trim() !== "") payload.condition = editCondition.trim();
                patchMut.mutate(payload);
              }}
              disabled={patchMut.isPending || !editName.trim()}
              className="bg-primary text-primary-foreground focus-ring"
              style={{ padding: "6px 12px", borderRadius: 6, border: "none", cursor: "pointer" }}
            >
              {patchMut.isPending ? "Saving..." : "Save"}
            </button>
            <span className="text-muted-foreground" style={{ fontSize: 11 }}>Uses If-Match: {asset.version} for optimistic concurrency</span>
          </div>
        </div>
      )}

      {error && <div className="text-danger" style={{ fontSize: 13, marginBottom: 12 }}>{error}</div>}

      {expiryAssertion?.review_state === "needs_evidence" && (
        <ExpiryEntryForm assetId={asset.id} householdId={householdId} evidenceIds={evidence.map((item) => item.id)} />
      )}

      <h3>Evidence</h3>
      <EvidenceGallery evidence={evidence} householdId={householdId} />
      <div style={{ marginTop: 12, display: "flex", gap: 8, alignItems: "center" }}>
        <input id="attach-input" type="file" multiple accept="image/*,.pdf" onChange={(e) => setAttachFiles(e.target.files)} />
        <button
          onClick={() => attachMut.mutate()}
          disabled={attachMut.isPending || !attachFiles?.length}
          className={`${attachFiles?.length ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"} border-border focus-ring`}
          style={{ padding: "6px 12px", borderRadius: 6, borderStyle: "solid", borderWidth: 1, cursor: "pointer" }}
        >
          {attachMut.isPending ? "Attaching..." : "Attach evidence"}
        </button>
      </div>

      <h3 style={{ marginTop: 24 }}>Assertions (provenance)</h3>
      {assertions.length === 0 ? (
        <div className="text-muted-foreground" style={{ fontSize: 13 }}>No assertions</div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr>
              <th className="border-border" style={{ textAlign: "left", borderBottomStyle: "solid", borderBottomWidth: 1, padding: 6 }}>Field</th>
              <th className="border-border" style={{ textAlign: "left", borderBottomStyle: "solid", borderBottomWidth: 1, padding: 6 }}>Value</th>
              <th className="border-border" style={{ textAlign: "left", borderBottomStyle: "solid", borderBottomWidth: 1, padding: 6 }}>Source</th>
              <th className="border-border" style={{ textAlign: "left", borderBottomStyle: "solid", borderBottomWidth: 1, padding: 6 }}>State</th>
              <th className="border-border" style={{ textAlign: "left", borderBottomStyle: "solid", borderBottomWidth: 1, padding: 6 }}>Confidence</th>
              <th className="border-border" style={{ textAlign: "left", borderBottomStyle: "solid", borderBottomWidth: 1, padding: 6 }}>Evidence</th>
            </tr>
          </thead>
          <tbody>
            {assertions.map((a) => (
              <tr key={a.id}>
                <td className="border-border font-mono" style={{ padding: 6, borderBottomStyle: "solid", borderBottomWidth: 1, fontSize: 12 }}>{a.field_path}</td>
                <td className="border-border" style={{ padding: 6, borderBottomStyle: "solid", borderBottomWidth: 1 }}>{String(a.value ?? "")}</td>
                <td className="border-border" style={{ padding: 6, borderBottomStyle: "solid", borderBottomWidth: 1 }}>{a.source_type}</td>
                <td className="border-border" style={{ padding: 6, borderBottomStyle: "solid", borderBottomWidth: 1 }}>
                  <ProvenanceBadge state={a.review_state} />
                </td>
                <td className="border-border" style={{ padding: 6, borderBottomStyle: "solid", borderBottomWidth: 1 }}>{a.confidence != null ? String(a.confidence) : "—"}</td>
                <td className="border-border text-muted-foreground" style={{ padding: 6, borderBottomStyle: "solid", borderBottomWidth: 1, fontSize: 11 }}>
                  {a.source_evidence_ids?.length ? a.source_evidence_ids.join(", ").slice(0, 40) : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <h3 style={{ marginTop: 24 }}>Audit history</h3>
      {audits.length === 0 ? (
        <div className="text-muted-foreground" style={{ fontSize: 13 }}>No audit events</div>
      ) : (
        <ul style={{ fontSize: 12, paddingLeft: 18 }}>
          {audits.map((e) => (
            <li key={e.id} style={{ marginBottom: 4 }}>
              <span className="font-mono">{e.action}</span> by {e.actor} — {e.timestamp || ""}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
