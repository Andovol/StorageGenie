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
        borderRadius: 4,
        fontSize: 12,
        display: "inline-block",
      }}
    >
      {state}
    </span>
  );
}
