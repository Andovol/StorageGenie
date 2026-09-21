import { useCallback, useEffect, useState } from "react";
import { apiPost, uploadEvidence } from "../api/client";

type Props = {
  householdId: string;
  onCreated: (id: string) => void;
};

type PreviewFile = { file: File; shaPreview: string | null };

async function sha256Hex(file: File): Promise<string> {
  const buf = await file.arrayBuffer();
  const hash = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export function AssetForm({ householdId, onCreated }: Props) {
  const [displayName, setDisplayName] = useState("");
  const [assetType, setAssetType] = useState("unknown");
  const [quantity, setQuantity] = useState("");
  const [unit, setUnit] = useState("");
  const [condition, setCondition] = useState("");
  const [previewFiles, setPreviewFiles] = useState<PreviewFile[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addFiles = useCallback(async (files: FileList | File[]) => {
    const arr = Array.from(files);
    const withSha: PreviewFile[] = await Promise.all(
      arr.map(async (f) => {
        try {
          const sha = await sha256Hex(f);
          return { file: f, shaPreview: sha.slice(0, 16) + "…" };
        } catch {
          return { file: f, shaPreview: null };
        }
      })
    );
    setPreviewFiles((prev) => [...prev, ...withSha]);
  }, []);

  const onDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (e.dataTransfer.files?.length) await addFiles(e.dataTransfer.files);
    },
    [addFiles]
  );

  useEffect(() => {
    const onPaste = async (e: ClipboardEvent) => {
      const files = e.clipboardData?.files;
      if (files && files.length) {
        e.preventDefault();
        await addFiles(files);
      }
    };
    window.addEventListener("paste", onPaste);
    return () => window.removeEventListener("paste", onPaste);
  }, [addFiles]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!displayName.trim() && previewFiles.length === 0) {
      setError("Add a photo or a display name");
      return;
    }
    if (!householdId) {
      setError("Household not selected");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const evidenceIds: string[] = [];
      for (const pf of previewFiles) {
        const ev = await uploadEvidence(householdId, pf.file);
        evidenceIds.push(ev.id);
      }
      const payload: Record<string, unknown> = {
        asset_type: assetType,
      };
      const trimmedName = displayName.trim();
      if (trimmedName) payload.display_name = trimmedName;
      if (quantity !== "") {
        const q = Number(quantity);
        if (!Number.isNaN(q)) payload.quantity = q;
      }
      if (unit.trim()) payload.unit = unit.trim();
      if (condition.trim()) payload.condition = condition.trim();
      if (evidenceIds.length) payload.evidence_ids = evidenceIds;

      const asset = await apiPost<{ id: string }>(
        "/v1/assets",
        payload,
        { household_id: householdId },
        { "Idempotency-Key": crypto.randomUUID() }
      );
      onCreated(asset.id);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12, maxWidth: 520 }}>
      <label style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        <span>Display name (optional)</span>
        <input
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          className="bg-background text-foreground border-border focus-ring"
          style={{ width: "100%", padding: 8, borderStyle: "solid", borderWidth: 1, borderRadius: 6 }}
          placeholder="e.g. Hammer"
        />
        <span className="text-muted-foreground" style={{ fontSize: 11 }}>Left blank, we use the photo's filename</span>
      </label>
      <label style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        <span>Asset type</span>
        <select value={assetType} onChange={(e) => setAssetType(e.target.value)} style={{ width: "100%", padding: 8, borderRadius: 6 }}>
          <option value="unknown">unknown</option>
          <option value="equipment">equipment</option>
          <option value="product">product</option>
          <option value="component">component</option>
          <option value="consumable">consumable</option>
          <option value="container">container</option>
          <option value="document">document</option>
          <option value="collection">collection</option>
        </select>
      </label>
      <div style={{ display: "flex", gap: 12 }}>
        <label style={{ flex: 1, display: "flex", flexDirection: "column", gap: 4 }}>
          <span>Quantity</span>
          <input value={quantity} onChange={(e) => setQuantity(e.target.value)} type="number" step="any" className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderStyle: "solid", borderWidth: 1, borderRadius: 6 }} />
        </label>
        <label style={{ flex: 1, display: "flex", flexDirection: "column", gap: 4 }}>
          <span>Unit</span>
          <input value={unit} onChange={(e) => setUnit(e.target.value)} placeholder="pcs, kg…" className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderStyle: "solid", borderWidth: 1, borderRadius: 6 }} />
        </label>
        <label style={{ flex: 1, display: "flex", flexDirection: "column", gap: 4 }}>
          <span>Condition</span>
          <input value={condition} onChange={(e) => setCondition(e.target.value)} placeholder="new, used…" className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderStyle: "solid", borderWidth: 1, borderRadius: 6 }} />
        </label>
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        className={dragOver ? "border-primary bg-accent" : "border-border bg-card-muted"}
        style={{
          borderStyle: "dashed",
          borderWidth: 2,
          borderRadius: 8,
          padding: 16,
          textAlign: "center",
        }}
      >
        <div className="text-muted-foreground" style={{ fontSize: 13, marginBottom: 8 }}>Drag &amp; drop photos here, click to select, or paste</div>
        <input
          type="file"
          multiple
          accept="image/*,.pdf"
          onChange={async (e) => {
            if (e.target.files?.length) await addFiles(e.target.files);
          }}
        />
        <label className="text-muted-foreground" style={{ display: "inline-flex", flexDirection: "column", gap: 4, marginTop: 12, fontSize: 13 }}>
          Take a photo
          <input
            type="file"
            accept="image/*"
            capture="environment"
            onChange={async (e) => {
              if (e.target.files?.length) await addFiles(e.target.files);
            }}
          />
        </label>
        {previewFiles.length > 0 && (
          <ul style={{ textAlign: "left", marginTop: 12, paddingLeft: 16 }}>
            {previewFiles.map((pf, i) => (
              <li key={i} style={{ fontSize: 12, marginBottom: 4 }}>
                {pf.file.name} — {(pf.file.size / 1024).toFixed(1)} KB {pf.shaPreview && <span className="text-muted-foreground">SHA {pf.shaPreview}</span>}
                <button type="button" onClick={() => setPreviewFiles((prev) => prev.filter((_, idx) => idx !== i))} style={{ marginLeft: 8, fontSize: 11 }}>
                  remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {error && <div className="text-danger" style={{ fontSize: 13 }}>{error}</div>}
      <button type="submit" disabled={submitting} className="bg-primary text-primary-foreground focus-ring" style={{ padding: "10px 16px", borderRadius: 6, border: "none", cursor: submitting ? "not-allowed" : "pointer" }}>
        {submitting ? "Creating..." : "Create asset"}
      </button>
    </form>
  );
}
