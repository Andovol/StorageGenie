import type { PlanningSuggestion } from "../api/types";

type Props = {
  suggestion: PlanningSuggestion;
  busy?: boolean;
  onConfirm: (id: string) => void;
  onDismiss: (id: string) => void;
};

function refLabel(ref: PlanningSuggestion["backing_refs"][number]): string {
  const detail = ref.label || ref.field_path || ref.id || ref.value;
  return detail ? `${ref.type}: ${String(detail)}` : ref.type;
}

export function PlanningSuggestionCard({ suggestion, busy, onConfirm, onDismiss }: Props) {
  const rationale = suggestion.body?.rationale ?? [];
  return (
    <div
      style={{
        padding: 12,
        border: "1px solid #e5e7eb",
        borderRadius: 8,
        background: "#fff",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
        <div>
          <strong>{suggestion.title}</strong>
          <div style={{ fontSize: 12, color: "#6b7280" }}>
            {suggestion.kind} · {suggestion.status}
          </div>
        </div>
        {suggestion.status === "pending" && (
          <div style={{ display: "flex", gap: 8, alignSelf: "flex-start" }}>
            <button
              type="button"
              onClick={() => onConfirm(suggestion.id)}
              disabled={busy}
            >
              Confirm
            </button>
            <button
              type="button"
              onClick={() => onDismiss(suggestion.id)}
              disabled={busy}
            >
              Dismiss
            </button>
          </div>
        )}
      </div>
      {rationale.length > 0 && (
        <ul style={{ margin: "8px 0 0 16px", fontSize: 13, color: "#374151" }}>
          {rationale.map((reason, index) => (
            <li key={index}>{reason}</li>
          ))}
        </ul>
      )}
      <div style={{ marginTop: 8, fontSize: 12, color: "#6b7280" }}>
        Backing evidence:{" "}
        {suggestion.backing_refs.length === 0
          ? "none"
          : suggestion.backing_refs.map((ref, index) => (
              <span key={index} style={{ marginRight: 8 }}>
                [{refLabel(ref)}]
              </span>
            ))}
      </div>
    </div>
  );
}
