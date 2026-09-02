import { Link } from "react-router-dom";
import type { Asset } from "../api/types";
import { ProvenanceBadge } from "./ProvenanceBadge";

export function AssetCard({ asset, householdId }: { asset: Asset; householdId: string }) {
  const base = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  const thumbEvidence = (asset as unknown as { evidence?: { id: string }[] }).evidence?.[0];
  const thumbUrl = thumbEvidence
    ? `${base}/v1/evidence/${thumbEvidence.id}/thumb/256?household_id=${householdId}`
    : null;
  const evidenceCount = (asset as unknown as { evidence?: unknown[] }).evidence?.length ?? 0;
  const acceptedCount = asset.assertions
    ? asset.assertions.filter((a) => a.review_state === "accepted").length
    : undefined;

  return (
    <Link
      to={`/assets/${asset.id}?household_id=${householdId}`}
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: 8,
        padding: 12,
        display: "block",
        textDecoration: "none",
        color: "inherit",
        background: "white",
      }}
    >
      {thumbUrl ? (
        <img
          src={thumbUrl}
          alt={asset.display_name}
          style={{ width: "100%", height: 120, objectFit: "cover", borderRadius: 6, marginBottom: 8, background: "#f3f4f6" }}
          onError={(e) => ((e.target as HTMLImageElement).style.display = "none")}
        />
      ) : (
        <div
          style={{
            width: "100%",
            height: 120,
            borderRadius: 6,
            marginBottom: 8,
            background: "#f3f4f6",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#9ca3af",
            fontSize: 12,
          }}
        >
          no image
        </div>
      )}
      <div style={{ fontWeight: 600, fontSize: 14, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
        {asset.display_name}
      </div>
      <div style={{ fontSize: 12, color: "#6b7280" }}>
        {asset.asset_type} · {asset.status}
      </div>
      <div style={{ display: "flex", gap: 6, marginTop: 6, alignItems: "center", flexWrap: "wrap" }}>
        <span style={{ fontSize: 11, color: "#6b7280" }}>{evidenceCount} evidence</span>
        {acceptedCount !== undefined && (
          <span style={{ fontSize: 11 }}>
            <ProvenanceBadge state={`${acceptedCount} accepted`} />
          </span>
        )}
        {asset.version ? <span style={{ fontSize: 11, color: "#9ca3af" }}>v{asset.version}</span> : null}
      </div>
    </Link>
  );
}
