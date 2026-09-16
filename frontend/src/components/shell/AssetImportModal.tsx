import { useCallback, useEffect, useRef, useState, type CSSProperties } from "react";
import { useNavigate } from "react-router-dom";
import { X } from "lucide-react";
import { apiPost, uploadEvidence } from "../../api/client";

/**
 * DQ9 import dialog. It drives the EXISTING deterministic import pipeline:
 * every staged file is uploaded to `/v1/evidence`, one `POST /v1/imports`
 * creates the job (single `Idempotency-Key`), and `POST /v1/imports/{id}/run`
 * executes it when auto-detect is checked. No model is called from here.
 */

const ACCEPTED_MIME = ["image/png", "image/jpeg", "image/webp"];
const ACCEPTED_EXT = /\.(png|jpe?g|webp)$/i;

// DQ9 names 25 MB as the target; the server enforces 20 MB today (`config.py:11`).
export const DQ9_TARGET_MB = 25;
export const SERVER_CAP_MB = 20;

type Rejected = { name: string; reason: string };

function isAccepted(file: File): boolean {
  const type = file.type.toLowerCase();
  if (type) return ACCEPTED_MIME.includes(type);
  return ACCEPTED_EXT.test(file.name);
}

function formatKb(size: number): string {
  return `${(size / 1024).toFixed(1)} KB`;
}

export type AssetImportModalProps = {
  householdId: string;
  onClose: () => void;
};

const panelStyle: CSSProperties = {
  position: "fixed",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  zIndex: 41,
  width: "min(560px, 92vw)",
  maxHeight: "88vh",
  overflowY: "auto",
  borderStyle: "solid",
  borderWidth: 1,
  borderRadius: 12,
  padding: 20,
};

export function AssetImportModal({ householdId, onClose }: AssetImportModalProps) {
  const navigate = useNavigate();
  const closeRef = useRef<HTMLButtonElement>(null);
  const restoreRef = useRef<HTMLElement | null>(
    typeof document !== "undefined" ? (document.activeElement as HTMLElement | null) : null
  );

  const [staged, setStaged] = useState<File[]>([]);
  const [rejected, setRejected] = useState<Rejected[]>([]);
  const [autoDetect, setAutoDetect] = useState(true);
  const [dragOver, setDragOver] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    closeRef.current?.focus();
  }, []);

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        onClose();
      }
    };
    document.addEventListener("keydown", handler);
    return () => {
      document.removeEventListener("keydown", handler);
      restoreRef.current?.focus?.();
    };
  }, [onClose]);

  const addFiles = useCallback((incoming: FileList | File[]) => {
    const accepted: File[] = [];
    const bad: Rejected[] = [];
    for (const file of Array.from(incoming)) {
      if (isAccepted(file)) {
        accepted.push(file);
      } else {
        bad.push({
          name: file.name,
          reason: file.type ? `unsupported type ${file.type}` : "unsupported type",
        });
      }
    }
    if (accepted.length) setStaged((prev) => [...prev, ...accepted]);
    if (bad.length) setRejected((prev) => [...prev, ...bad]);
  }, []);

  useEffect(() => {
    const onPaste = (event: ClipboardEvent) => {
      const files = event.clipboardData?.files;
      if (files && files.length) {
        event.preventDefault();
        addFiles(files);
      }
    };
    window.addEventListener("paste", onPaste);
    return () => window.removeEventListener("paste", onPaste);
  }, [addFiles]);

  const removeAt = (index: number) => {
    setStaged((prev) => prev.filter((_, i) => i !== index));
  };

  const cancel = () => {
    setStaged([]);
    setRejected([]);
    onClose();
  };

  const process = async () => {
    if (!staged.length || processing) return;
    setProcessing(true);
    setError(null);
    try {
      const evidenceIds: string[] = [];
      for (const file of staged) {
        const evidence = await uploadEvidence(householdId, file);
        evidenceIds.push(evidence.id);
      }
      const job = await apiPost<{ id: string }>(
        "/v1/imports",
        { evidence_ids: evidenceIds, config: {} },
        { household_id: householdId },
        { "Idempotency-Key": crypto.randomUUID() }
      );
      if (autoDetect) {
        await apiPost(`/v1/imports/${job.id}/run`, {}, { household_id: householdId });
      }
      setStaged([]);
      onClose();
      navigate("/inbox");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
      setProcessing(false);
    }
  };

  return (
    <div className="font-sans">
      <div
        data-testid="import-backdrop"
        className="bg-background"
        aria-hidden="true"
        onClick={cancel}
        style={{ position: "fixed", inset: 0, opacity: 0.5, zIndex: 40 }}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Import assets"
        className="bg-card text-foreground border-border"
        style={panelStyle}
      >
        <header style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
          <h2 style={{ margin: 0, fontSize: 18, flex: 1 }}>Import assets</h2>
          <button
            ref={closeRef}
            type="button"
            aria-label="Close import dialog"
            onClick={cancel}
            className="text-muted-foreground focus-ring"
            style={{ background: "none", border: "none", cursor: "pointer", padding: 4, borderRadius: 4 }}
          >
            <X size={18} aria-hidden="true" />
          </button>
        </header>

        <div
          data-testid="import-dropzone"
          onDragOver={(event) => {
            event.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(event) => {
            event.preventDefault();
            setDragOver(false);
            if (event.dataTransfer.files?.length) addFiles(event.dataTransfer.files);
          }}
          className="bg-card-muted"
          style={{
            borderStyle: "dashed",
            borderWidth: 2,
            borderColor: dragOver ? "hsl(var(--primary))" : "hsl(var(--border))",
            borderRadius: 8,
            padding: 16,
            textAlign: "center",
          }}
        >
          <p className="text-muted-foreground" style={{ margin: "0 0 10px", fontSize: 13 }}>
            Drag &amp; drop photos here, choose files, or paste (Ctrl+V / ⌘V).
          </p>
          <input
            type="file"
            multiple
            aria-label="Choose image files"
            accept="image/png,image/jpeg,image/webp"
            onChange={(event) => {
              if (event.target.files?.length) addFiles(event.target.files);
              event.target.value = "";
            }}
          />
          <p data-testid="import-size-note" className="text-muted-foreground" style={{ margin: "10px 0 0", fontSize: 11 }}>
            PNG, JPG or WebP. DQ9 target: up to {DQ9_TARGET_MB} MB per file — this server currently
            accepts up to {SERVER_CAP_MB} MB.
          </p>
        </div>

        {rejected.length > 0 && (
          <div
            role="alert"
            data-testid="rejected-files"
            style={{ marginTop: 12, color: "hsl(var(--badge-failed-fg))", fontSize: 12 }}
          >
            <strong>
              Skipped {rejected.length} file{rejected.length === 1 ? "" : "s"}:
            </strong>
            <ul style={{ margin: "4px 0 0", paddingLeft: 18 }}>
              {rejected.map((entry, index) => (
                <li key={`${entry.name}-${index}`}>
                  {entry.name} — {entry.reason}
                </li>
              ))}
            </ul>
          </div>
        )}

        <label style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 16, fontSize: 13 }}>
          <input
            type="checkbox"
            checked={autoDetect}
            onChange={(event) => setAutoDetect(event.target.checked)}
          />
          Automatically detect items and isolate cutouts
        </label>
        <p data-testid="auto-detect-help" className="text-muted-foreground" style={{ margin: "4px 0 0 24px", fontSize: 11 }}>
          {autoDetect
            ? "Checked: the import job is created and run immediately."
            : "Unchecked: the job is created but not run — it waits in the Inbox until you run it there."}
        </p>

        <section style={{ marginTop: 16 }}>
          <h3 data-testid="queue-count" style={{ margin: "0 0 8px", fontSize: 14 }}>
            Pending queue ({staged.length})
          </h3>
          {staged.length === 0 ? (
            <p data-testid="queue-empty" className="text-muted-foreground" style={{ margin: 0, fontSize: 12 }}>
              No files staged yet.
            </p>
          ) : (
            <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: 6 }}>
              {staged.map((file, index) => (
                <li
                  key={`${file.name}-${index}`}
                  data-testid="queue-item"
                  className="bg-card-muted"
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "6px 10px",
                    borderRadius: 6,
                    fontSize: 12,
                  }}
                >
                  <span style={{ flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {file.name}
                  </span>
                  <span className="text-muted-foreground font-mono">{formatKb(file.size)}</span>
                  <span style={{ color: "hsl(var(--badge-processed-fg))", fontWeight: 600 }}>Ready</span>
                  <button
                    type="button"
                    aria-label={`Remove ${file.name}`}
                    onClick={() => removeAt(index)}
                    className="focus-ring"
                    style={{
                      background: "none",
                      border: "none",
                      cursor: "pointer",
                      color: "hsl(var(--muted-foreground))",
                      fontSize: 12,
                    }}
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        {error && (
          <div role="alert" style={{ marginTop: 12, color: "hsl(var(--badge-failed-fg))", fontSize: 13 }}>
            {error}
          </div>
        )}

        <footer style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 20 }}>
          <button
            type="button"
            onClick={cancel}
            className="bg-card text-foreground border-border focus-ring"
            style={{ padding: "6px 12px", borderRadius: 6, borderStyle: "solid", borderWidth: 1, cursor: "pointer" }}
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={process}
            disabled={staged.length === 0 || processing}
            className="bg-primary text-primary-foreground focus-ring"
            style={{
              padding: "6px 12px",
              borderRadius: 6,
              border: "none",
              cursor: staged.length === 0 || processing ? "not-allowed" : "pointer",
            }}
          >
            {processing ? "Processing…" : `Process ${staged.length} Item${staged.length === 1 ? "" : "s"}`}
          </button>
        </footer>
      </div>
    </div>
  );
}
