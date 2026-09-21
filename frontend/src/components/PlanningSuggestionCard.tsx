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
      className="bg-card border-border"
      style={{
        padding: 12,
        borderStyle: "solid",
        borderWidth: 1,
        borderRadius: 8,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
        <div>
          <strong>{suggestion.title}</strong>
          <div className="text-muted-foreground" style={{ fontSize: 12 }}>
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
        <ul className="text-foreground" style={{ margin: "8px 0 0 16px", fontSize: 13 }}>
          {rationale.map((reason, index) => (
            <li key={index}>{reason}</li>
          ))}
        </ul>
      )}
      <div className="text-muted-foreground" style={{ marginTop: 8, fontSize: 12 }}>
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
