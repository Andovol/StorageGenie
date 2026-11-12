import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiGet, apiPost, uploadEvidence } from "../api/client";
import type { Asset, AssetListResponse } from "../api/types";
import { expiryDateFrom, formatUseByDate } from "../lib/labels";
import { CONTROL_STYLE, THEMED_CONTROL_CLASS } from "./shell/CatalogToolbar";
import { SERVER_CAP_LABEL } from "./shell/AssetImportModal";

type Props = {
  householdId: string;
  onCreated: (id: string) => void;
};

type PreviewFile = { file: File; shaPreview: string | null };

/** SG-304 G1: a live item the typed name matches, with its date when it has one. */
type SamePack = { id: string; name: string; expiry: string | null };

// Items in these states are not live; the list read already hides ARCHIVED.
const NOT_LIVE_STATUSES = new Set(["ARCHIVED", "DISPOSED", "MERGED"]);

/**
 * SG-304 G1: live items whose name equals the typed name (trimmed, case-
 * insensitive). Uses the existing list read (`q` = FTS on display_name) and the
 * existing detail read for each match's date. Same name is NOT identity: this
 * only offers the existing item; the caller decides.
 */
async function findSameNamePacks(householdId: string, name: string): Promise<SamePack[]> {
  const wanted = name.trim().toLowerCase();
  const list = await apiGet<AssetListResponse>("/v1/assets", {
    household_id: householdId,
    q: name.trim(),
    limit: "100",
  });
  const matches = list.items.filter(
    (item) =>
      (item.display_name ?? "").trim().toLowerCase() === wanted && !NOT_LIVE_STATUSES.has(item.status)
  );
  return Promise.all(
    matches.map(async (item) => {
      let expiry: string | null = null;
      try {
        const detail = await apiGet<Asset>(`/v1/assets/${item.id}`, { household_id: householdId });
        expiry = expiryDateFrom(detail.assertions);
      } catch {
        expiry = null;
      }
      return { id: item.id, name: item.display_name ?? name.trim(), expiry };
    })
  );
}

/**
 * SG-105 G2: the real `<input type="file">` stays in the DOM (and stays
 * focusable/announced), but is visually hidden behind its label so no native
 * white picker button leaks through the dark theme.
 */
const VISUALLY_HIDDEN: React.CSSProperties = {
  position: "absolute",
  width: 1,
  height: 1,
  padding: 0,
  margin: -1,
  overflow: "hidden",
  clip: "rect(0 0 0 0)",
  whiteSpace: "nowrap",
  borderWidth: 0,
};

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
  const [samePacks, setSamePacks] = useState<SamePack[] | null>(null);

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
    // SG-304 G1: a live item with the same name is offered before anything is
    // uploaded or created. A failed lookup never blocks the create (today's path).
    const typedName = displayName.trim();
    if (typedName) {
      setSubmitting(true);
      setError(null);
      let matches: SamePack[] = [];
      try {
        matches = await findSameNamePacks(householdId, typedName);
      } catch {
        matches = [];
      }
      setSubmitting(false);
      if (matches.length > 0) {
        setSamePacks(matches);
        return;
      }
    }
    await createItem();
  }

  async function createItem() {
    if (!householdId) return;
    setSamePacks(null);
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
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
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
        <span>Kind of item</span>
        <select className={THEMED_CONTROL_CLASS} value={assetType} onChange={(e) => setAssetType(e.target.value)} style={{ ...CONTROL_STYLE, width: "100%", padding: 8 }}>
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
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <label style={{ flex: "1 1 140px", display: "flex", flexDirection: "column", gap: 4 }}>
          <span>Quantity</span>
          <input value={quantity} onChange={(e) => setQuantity(e.target.value)} type="number" step="any" className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderStyle: "solid", borderWidth: 1, borderRadius: 6, minWidth: 0 }} />
        </label>
        <label style={{ flex: "1 1 140px", display: "flex", flexDirection: "column", gap: 4 }}>
          <span>Unit</span>
          <input value={unit} onChange={(e) => setUnit(e.target.value)} placeholder="pcs, kg…" className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderStyle: "solid", borderWidth: 1, borderRadius: 6, minWidth: 0 }} />
        </label>
        <label style={{ flex: "1 1 140px", display: "flex", flexDirection: "column", gap: 4 }}>
          <span>Condition</span>
          <input value={condition} onChange={(e) => setCondition(e.target.value)} placeholder="new, used…" className="bg-background text-foreground border-border focus-ring" style={{ padding: 8, borderStyle: "solid", borderWidth: 1, borderRadius: 6, minWidth: 0 }} />
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
        <div style={{ display: "inline-flex", gap: 8, flexWrap: "wrap", justifyContent: "center" }}>
          <label
            className={`${THEMED_CONTROL_CLASS} file-pick`}
            style={{ ...CONTROL_STYLE, display: "inline-flex", alignItems: "center" }}
          >
            Choose files
            <input
              type="file"
              multiple
              accept="image/*,.pdf"
              className={THEMED_CONTROL_CLASS}
              style={VISUALLY_HIDDEN}
              onChange={async (e) => {
                if (e.target.files?.length) await addFiles(e.target.files);
              }}
            />
          </label>
          <label
            className={`${THEMED_CONTROL_CLASS} file-pick`}
            style={{ ...CONTROL_STYLE, display: "inline-flex", alignItems: "center" }}
          >
            Take a photo
            <input
              type="file"
              accept="image/*"
              capture="environment"
              className={THEMED_CONTROL_CLASS}
              style={VISUALLY_HIDDEN}
              onChange={async (e) => {
                if (e.target.files?.length) await addFiles(e.target.files);
              }}
            />
          </label>
        </div>
        <p className="text-muted-foreground" data-testid="manual-formats-note" style={{ fontSize: 11, margin: "10px 0 0" }}>
          PNG, JPG, WebP, TIFF, HEIC or PDF, up to {SERVER_CAP_LABEL} per file.
        </p>
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

      {samePacks && samePacks.length > 0 && (
        <div role="status" data-testid="same-name-warning" className="bg-accent border-accent" style={{ padding: 10, borderStyle: "solid", borderWidth: 1, borderRadius: 6, fontSize: 13 }}>
          {samePacks.length === 1 ? (
            <div>
              You already have <strong>{samePacks[0].name}</strong>
              {samePacks[0].expiry ? ` (use by ${formatUseByDate(samePacks[0].expiry)}).` : " (no date set)."}
            </div>
          ) : (
            <>
              <div>You already have these:</div>
              <ul style={{ margin: "6px 0", paddingLeft: 18 }}>
                {samePacks.map((pack) => (
                  <li key={pack.id}>
                    <strong>{pack.name}</strong>
                    {pack.expiry ? ` (use by ${formatUseByDate(pack.expiry)})` : " (no date set)"}{" "}
                    <Link to={`/assets/${pack.id}?household_id=${householdId}`} className="text-link focus-ring">Open it</Link>
                  </li>
                ))}
              </ul>
            </>
          )}
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 8 }}>
            <button type="button" onClick={() => void createItem()} disabled={submitting} className="text-link focus-ring" style={{ fontSize: 13 }}>
              Add another pack
            </button>
            {samePacks.length === 1 && (
              <Link to={`/assets/${samePacks[0].id}?household_id=${householdId}`} className="text-link focus-ring" style={{ fontSize: 13 }}>
                Open it
              </Link>
            )}
            <button type="button" onClick={() => setSamePacks(null)} disabled={submitting} className="text-link focus-ring" style={{ fontSize: 13 }}>
              Cancel
            </button>
          </div>
        </div>
      )}
      {error && <div className="text-danger" style={{ fontSize: 13 }}>{error}</div>}
      <button type="submit" disabled={submitting} className="bg-primary text-primary-foreground focus-ring" style={{ padding: "10px 16px", borderRadius: 6, border: "none", cursor: submitting ? "not-allowed" : "pointer" }}>
        {submitting ? "Creating..." : "Create asset"}
      </button>
    </form>
  );
}
