import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchAiSettings, updateAiModel } from "../api/client";
import type { AiSettings } from "../api/types";

export function SettingsPage() {
  const qc = useQueryClient();
  const settings = useQuery<AiSettings>({ queryKey: ["ai-settings"], queryFn: fetchAiSettings });
  const update = useMutation({
    mutationFn: (modelId: string) => updateAiModel(modelId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["ai-settings"] }),
  });

  return (
    <div style={{ padding: 24 }}>
      <h1>Settings</h1>
      <p style={{ color: "#6b7280", fontSize: 13 }}>
        Phase 0 — household and connection settings. API base: {import.meta.env.VITE_API_BASE || "http://localhost:8003"}
      </p>

      <section
        style={{
          marginTop: 16,
          padding: 12,
          border: "1px solid #e5e7eb",
          borderRadius: 8,
          maxWidth: 520,
        }}
      >
        <h2 style={{ fontSize: 15, margin: 0 }}>AI model</h2>
        <p style={{ color: "#6b7280", fontSize: 12, marginTop: 4 }}>
          Effective model: {settings.data?.model_id ?? "loading…"}
        </p>
        {settings.isError && <div role="alert">{String(settings.error)}</div>}
        <label htmlFor="ai-model">
          AI model
          <select
            id="ai-model"
            value={settings.data?.model_id ?? ""}
            disabled={!settings.data || update.isPending}
            onChange={(event) => update.mutate(event.target.value)}
            style={{ marginLeft: 8 }}
          >
            {(settings.data?.allowed_model_ids ?? []).map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </label>
        {update.isError && (
          <div role="alert" style={{ color: "#b91c1c", marginTop: 8 }}>
            {String(update.error)}
          </div>
        )}
      </section>

      <div style={{ marginTop: 16 }}>
        <button
          onClick={() => {
            localStorage.removeItem("household_id");
            window.location.reload();
          }}
          style={{ padding: "6px 12px", borderRadius: 6, border: "1px solid #d1d5db" }}
        >
          Clear household selection
        </button>
      </div>
    </div>
  );
}
