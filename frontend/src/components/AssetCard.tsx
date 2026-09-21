import { Link } from "react-router-dom";
import type { Asset } from "../api/types";
import { UNTITLED_ASSET_NAME } from "../types/product";
import { ProvenanceBadge } from "./ProvenanceBadge";

export function AssetCard({ asset, householdId }: { asset: Asset; householdId: string }) {
  const base = import.meta.env.VITE_API_BASE || "http://localhost:8003";
  const displayName = asset.display_name || UNTITLED_ASSET_NAME;
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
      className="bg-card border-border focus-ring"
      style={{
        borderStyle: "solid",
        borderWidth: 1,
        borderRadius: 8,
        padding: 12,
        display: "block",
        textDecoration: "none",
        color: "inherit",
      }}
    >
      {thumbUrl ? (
        <img
          src={thumbUrl}
          alt={displayName}
          className="bg-card-muted"
          style={{ width: "100%", height: 120, objectFit: "cover", borderRadius: 6, marginBottom: 8 }}
          onError={(e) => ((e.target as HTMLImageElement).style.display = "none")}
        />
      ) : (
        <div
          className="bg-card-muted text-muted-foreground"
          style={{
            width: "100%",
            height: 120,
            borderRadius: 6,
            marginBottom: 8,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 12,
          }}
        >
          no image
        </div>
      )}
      <div style={{ fontWeight: 600, fontSize: 14, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
        {displayName}
      </div>
      <div className="text-muted-foreground" style={{ fontSize: 12 }}>
        {asset.asset_type} · {asset.status}
      </div>
      <div style={{ display: "flex", gap: 6, marginTop: 6, alignItems: "center", flexWrap: "wrap" }}>
        <span className="text-muted-foreground" style={{ fontSize: 11 }}>{evidenceCount} evidence</span>
        {acceptedCount !== undefined && (
          <span style={{ fontSize: 11 }}>
            <ProvenanceBadge state={`${acceptedCount} accepted`} />
          </span>
        )}
        {asset.version ? <span className="text-muted-foreground" style={{ fontSize: 11 }}>v{asset.version}</span> : null}
      </div>
    </Link>
  );
}
