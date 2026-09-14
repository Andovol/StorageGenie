import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  confirmPlanningSuggestion,
  dismissPlanningSuggestion,
  fetchPlanningSuggestions,
  runPlanning,
} from "../api/client";
import type {
  Household,
  PlanningRunResult,
  PlanningSuggestionListResponse,
} from "../api/types";
import { PlanningSuggestionCard } from "../components/PlanningSuggestionCard";
import { useHouseholds } from "../hooks/useAssets";

const STATUS_OPTIONS = ["", "pending", "confirmed", "dismissed"] as const;

export function PlanningPage() {
  const { data: households } = useHouseholds();
  const [householdId, setHouseholdId] = useState(
    () => localStorage.getItem("household_id") || ""
  );
  const [status, setStatus] = useState("");
  const [message, setMessage] = useState("");
  const qc = useQueryClient();
  const effectiveHousehold = householdId || households?.[0]?.id || "";
  useEffect(() => {
    if (!householdId && households?.[0]) {
      setHouseholdId(households[0].id);
      localStorage.setItem("household_id", households[0].id);
    }
  }, [householdId, households]);

  const suggestions = useQuery<PlanningSuggestionListResponse>({
    queryKey: ["planning-suggestions", effectiveHousehold, status],
    queryFn: () => fetchPlanningSuggestions(effectiveHousehold, status || undefined),
    enabled: !!effectiveHousehold,
  });
  const run = useMutation({
    mutationFn: () => runPlanning(effectiveHousehold),
    onSuccess: (result: PlanningRunResult) => {
      setMessage(
        result.status === "skipped"
          ? `Planning did not run: ${result.reason ?? "skipped"}`
          : `Planning wrote ${result.suggestion_count} suggestion(s).`
      );
      qc.invalidateQueries({ queryKey: ["planning-suggestions", effectiveHousehold] });
    },
    onError: (error: unknown) => setMessage(String(error)),
  });
  const confirm = useMutation({
    mutationFn: (id: string) => confirmPlanningSuggestion(id, effectiveHousehold),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["planning-suggestions", effectiveHousehold] }),
  });
  const dismiss = useMutation({
    mutationFn: (id: string) => dismissPlanningSuggestion(id, effectiveHousehold),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["planning-suggestions", effectiveHousehold] }),
  });

  return (
    <div style={{ padding: 24, maxWidth: 900 }}>
      <div
        style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}
      >
        <h1>Planning</h1>
        <label>
          Household{" "}
          <select
            value={effectiveHousehold}
            onChange={(event) => {
              setHouseholdId(event.target.value);
              localStorage.setItem("household_id", event.target.value);
            }}
          >
            <option value="">Select household</option>
            {(households as Household[] | undefined)?.map((household) => (
              <option key={household.id} value={household.id}>
                {household.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      <p style={{ color: "#6b7280", fontSize: 13 }}>
        Suggestions are proposals only. Confirming or dismissing one changes no asset, job
        or setting; nothing is ever executed automatically.
      </p>

      <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 12 }}>
        <button
          type="button"
          onClick={() => run.mutate()}
          disabled={!effectiveHousehold || run.isPending}
        >
          {run.isPending ? "Running…" : "Run planning"}
        </button>
        <label>
          Status{" "}
          <select value={status} onChange={(event) => setStatus(event.target.value)}>
            {STATUS_OPTIONS.map((option) => (
              <option key={option || "all"} value={option}>
                {option || "all"}
              </option>
            ))}
          </select>
        </label>
      </div>
      {message && (
        <div role="alert" style={{ marginTop: 12, color: "#374151" }}>
          {message}
        </div>
      )}

      <section style={{ marginTop: 20, display: "grid", gap: 8 }}>
        {suggestions.isLoading && <div>Loading suggestions…</div>}
        {!suggestions.isLoading && suggestions.data?.items.length === 0 && (
          <div role="status">No planning suggestions yet.</div>
        )}
        {suggestions.data?.items.map((suggestion) => (
          <PlanningSuggestionCard
            key={suggestion.id}
            suggestion={suggestion}
            busy={confirm.isPending || dismiss.isPending}
            onConfirm={(id) => confirm.mutate(id)}
            onDismiss={(id) => dismiss.mutate(id)}
          />
        ))}
      </section>
    </div>
  );
}
