const REVIEW_STATE_LABELS: Record<string, string> = {
  accepted: "Kept",
  proposed: "Suggested",
  rejected: "Not kept",
  superseded: "Replaced",
};

function labelReviewState(state: string): string {
  const normalized = state?.toLowerCase() || "unknown";
  if (REVIEW_STATE_LABELS[normalized]) return REVIEW_STATE_LABELS[normalized];
  return normalized.replace(/[_.]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function ProvenanceBadge({ state }: { state: string }) {
  const normalized = state?.toLowerCase() || "unknown";
  const tone =
    normalized === "accepted"
      ? "badge-green"
      : normalized === "proposed"
        ? "badge-amber"
        : "badge-grey";
  return (
    <span
      className={tone}
      style={{
        padding: "2px 6px",
        borderRadius: 0,
        fontSize: 13,
        display: "inline-block",
      }}
    >
      {labelReviewState(state)}
    </span>
  );
}
