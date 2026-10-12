import { useState } from "react";

type Ev = { id: string; storage_key: string; sha256?: string; original_filename?: string };

export function EvidenceGallery({ evidence, householdId }: { evidence: Ev[]; householdId: string }) {
  const base = import.meta.env.VITE_API_BASE || "http://localhost:8003";
  const [failedIds, setFailedIds] = useState<Set<string>>(new Set());

  if (!evidence || evidence.length === 0) return <div className="text-muted-foreground">No evidence attached</div>;

  return (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
      {evidence.map((e) => {
        const name = e.original_filename || e.id;
        const ariaLabel = `View evidence file: ${name} (opens in new tab)`;
        const altText = e.original_filename ? `Evidence thumbnail for ${e.original_filename}` : `Evidence thumbnail ${e.id}`;
        const isFailed = failedIds.has(e.id);

        return (
          <a
            key={e.id}
            href={`${base}/v1/evidence/${e.id}/file?household_id=${householdId}`}
            target="_blank"
            rel="noreferrer"
            aria-label={ariaLabel}
            title={e.sha256 ? `SHA256: ${e.sha256}` : e.id}
            className="focus-ring border-border"
            style={{
              display: "inline-block",
              borderRadius: 6,
              borderStyle: "solid",
              borderWidth: 1,
              overflow: "hidden",
              textDecoration: "none",
            }}
          >
            {isFailed ? (
              <div
                className="bg-card-muted text-muted-foreground"
                style={{
                  width: 120,
                  height: 120,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 11,
                  padding: 4,
                  textAlign: "center",
                }}
              >
                Thumbnail unavailable
              </div>
            ) : (
              <img
                src={`${base}/v1/evidence/${e.id}/thumb/256?household_id=${householdId}`}
                alt={altText}
                style={{ width: 120, height: 120, objectFit: "cover", display: "block" }}
                onError={() => {
                  setFailedIds((prev) => new Set(prev).add(e.id));
                }}
              />
            )}
          </a>
        );
      })}
    </div>
  );
}
