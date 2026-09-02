export function ProvenanceBadge({ state }: { state: string }) {
  const normalized = state?.toLowerCase() || "unknown";
  const bg =
    normalized === "accepted"
      ? "#16a34a"
      : normalized === "proposed"
        ? "#f59e0b"
        : normalized === "needs_evidence"
          ? "#9ca3af"
          : normalized === "superseded"
            ? "#6b7280"
            : normalized === "rejected"
              ? "#dc2626"
              : "#6b7280";
  return (
    <span
      className={
        normalized === "accepted"
          ? "badge-green"
          : normalized === "proposed"
            ? "badge-amber"
            : "badge-grey"
      }
      style={{
        padding: "2px 6px",
        borderRadius: 4,
        fontSize: 12,
        background: bg,
        color: "white",
        display: "inline-block",
      }}
    >
      {state}
    </span>
  );
}
