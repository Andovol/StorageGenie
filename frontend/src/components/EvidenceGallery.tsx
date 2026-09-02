type Ev = { id: string; storage_key: string; sha256?: string; original_filename?: string };

export function EvidenceGallery({ evidence, householdId }: { evidence: Ev[]; householdId: string }) {
  const base = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  if (!evidence || evidence.length === 0) return <div style={{ color: "#9ca3af" }}>No evidence attached</div>;
  return (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
      {evidence.map((e) => (
        <a
          key={e.id}
          href={`${base}/v1/evidence/${e.id}/file?household_id=${householdId}`}
          target="_blank"
          rel="noreferrer"
          title={e.sha256 ? `SHA256: ${e.sha256}` : e.id}
        >
          <img
            src={`${base}/v1/evidence/${e.id}/thumb/256?household_id=${householdId}`}
            alt={e.original_filename || "evidence"}
            style={{ width: 120, height: 120, objectFit: "cover", borderRadius: 6, border: "1px solid #e5e7eb" }}
            onError={(ev) => ((ev.target as HTMLImageElement).style.display = "none")}
          />
        </a>
      ))}
    </div>
  );
}
