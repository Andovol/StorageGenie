import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchAiSettings, updateAiModel } from "../api/client";
import type { AiSettings } from "../api/types";
import { PageContainer } from "../components/shell/PageContainer";

export function SettingsPage() {
  const qc = useQueryClient();
  const settings = useQuery<AiSettings>({ queryKey: ["ai-settings"], queryFn: fetchAiSettings });
  const update = useMutation({
    mutationFn: (modelId: string) => updateAiModel(modelId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["ai-settings"] }),
  });

  return (
    <PageContainer className="text-foreground">
      <h1 className="page-header text-foreground">Settings</h1>
      <p className="text-muted-foreground" style={{ fontSize: 13 }}>
        Phase 0 — household and connection settings. API base: {import.meta.env.VITE_API_BASE || "http://localhost:8003"}
      </p>

      <section
        className="bg-card border-border"
        style={{
          marginTop: 16,
          padding: 12,
          borderStyle: "solid",
          borderWidth: 1,
          borderRadius: 8,
          maxWidth: 520,
        }}
      >
        <h2 style={{ fontSize: 15, margin: 0 }}>AI model</h2>
        <p className="text-muted-foreground" style={{ fontSize: 12, marginTop: 4 }}>
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
          <div role="alert" className="text-danger" style={{ marginTop: 8 }}>
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
          className="bg-card text-foreground border-border focus-ring"
          style={{ padding: "6px 12px", borderRadius: 6, borderStyle: "solid", borderWidth: 1, cursor: "pointer" }}
        >
          Clear household selection
        </button>
      </div>
    </PageContainer>
  );
}
