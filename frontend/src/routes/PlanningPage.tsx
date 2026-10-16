import { useState } from "react";
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
import { HouseholdSelector } from "../components/HouseholdSelector";
import { PlanningSuggestionCard } from "../components/PlanningSuggestionCard";
import { CONTROL_STYLE, THEMED_CONTROL_CLASS } from "../components/shell/CatalogToolbar";
import { PageContainer } from "../components/shell/PageContainer";
import { useHouseholdContext } from "../hooks/HouseholdContext";

const STATUS_OPTIONS = ["", "pending", "confirmed", "dismissed"] as const;

export function PlanningPage() {
  // SG-196 G1: selection state lives in the shared context; the household
  // failure branch now reads the context's error state.
  const {
    households,
    isError: householdsIsError,
    error: householdsError,
    householdId,
    setHouseholdId,
  } = useHouseholdContext();
  const [status, setStatus] = useState("");
  const [message, setMessage] = useState("");
  const qc = useQueryClient();
  const effectiveHousehold = householdId || households?.[0]?.id || "";

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
    <PageContainer className="text-foreground">
      <div
        style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: 12 }}
      >
        <h1 className="page-header text-foreground">Planning</h1>
        <HouseholdSelector
          value={effectiveHousehold}
          onChange={setHouseholdId}
          households={households as Household[] | undefined}
        />
      </div>
      {householdsIsError && (
        <div role="alert">Could not load households: {String(householdsError)}</div>
      )}
      <p className="text-muted-foreground" style={{ fontSize: 13 }}>
        Suggestions are proposals only. Confirming or dismissing one changes no asset, job
        or setting; nothing is ever executed automatically.
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center", marginTop: 12 }}>
        <button
          type="button"
          onClick={() => run.mutate()}
          disabled={!effectiveHousehold || run.isPending}
          className="bg-card text-foreground border-border focus-ring"
          style={CONTROL_STYLE}
        >
          {run.isPending ? "Running…" : "Run planning"}
        </button>
        <label>
          Status{" "}
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value)}
            className={THEMED_CONTROL_CLASS}
            style={CONTROL_STYLE}
          >
            {STATUS_OPTIONS.map((option) => (
              <option key={option || "all"} value={option}>
                {option || "all"}
              </option>
            ))}
          </select>
        </label>
      </div>
      {message && (
        <div role="alert" className="text-foreground" style={{ marginTop: 12 }}>
          {message}
        </div>
      )}

      <section style={{ marginTop: 20, display: "grid", gap: 8 }}>
        {suggestions.isLoading && <div>Loading suggestions…</div>}
        {suggestions.isError && (
          <div role="alert">Could not load planning suggestions: {String(suggestions.error)}</div>
        )}
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
    </PageContainer>
  );
}
