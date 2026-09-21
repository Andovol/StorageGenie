import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { fetchAnalyticsSummary, generateAnalyticsInsights } from "../api/client";
import type { AnalyticsInsightResult, AnalyticsSummary, Household } from "../api/types";
import { useHouseholds } from "../hooks/useAssets";

const EXPIRY_LABELS: Record<string, string> = {
  expired: "Expired",
  within_7_days: "Expiring within 7 days",
  within_30_days: "Expiring within 30 days",
  safe: "Safe (beyond 30 days)",
  unknown: "No active expiry date",
};

function CountRow({ label, value }: { label: string; value: number }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export function AnalyticsPage() {
  const { data: households } = useHouseholds();
  const [householdId, setHouseholdId] = useState(
    () => localStorage.getItem("household_id") || ""
  );
  const [message, setMessage] = useState("");
  const effectiveHousehold = householdId || households?.[0]?.id || "";
  useEffect(() => {
    if (!householdId && households?.[0]) {
      setHouseholdId(households[0].id);
      localStorage.setItem("household_id", households[0].id);
    }
  }, [householdId, households]);

  const summary = useQuery<AnalyticsSummary>({
    queryKey: ["analytics-summary", effectiveHousehold],
    queryFn: () => fetchAnalyticsSummary(effectiveHousehold),
    enabled: !!effectiveHousehold,
  });
  const insights = useMutation({
    mutationFn: () => generateAnalyticsInsights(effectiveHousehold),
    onSuccess: (result: AnalyticsInsightResult) => {
      if (result.status === "ok" && result.summary) {
        setMessage("");
      } else if (result.status === "ok") {
        setMessage("There is not enough recorded data to summarize yet.");
      } else {
        setMessage(`Summary did not run: ${result.reason ?? result.status}`);
      }
    },
    onError: (error: unknown) => setMessage(String(error)),
  });

  const data = summary.data;
  const insightResult = insights.data;

  return (
    <div style={{ padding: 24, maxWidth: 900 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Analytics</h1>
        <label>
          Household{" "}
          <select
            value={effectiveHousehold}
            onChange={(event) => {
              setHouseholdId(event.target.value);
              localStorage.setItem("household_id", event.target.value);
              setMessage("");
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
        These numbers are computed from your own recorded items. The summary is prose only —
        it is grounded in the numbers shown, takes no action, and is never refreshed
        automatically.
      </p>

      {summary.isLoading && <div>Loading analytics…</div>}
      {!summary.isLoading && data && data.assets.total === 0 && (
        <div role="status">No analytics data yet for this household.</div>
      )}

      {data && data.assets.total > 0 && (
        <div
          style={{
            marginTop: 16,
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: 16,
          }}
        >
          <section aria-label="Assets">
            <h2 style={{ fontSize: 15 }}>Assets</h2>
            <CountRow label="Total" value={data.assets.total} />
            <CountRow label="Active" value={data.assets.active} />
          </section>
          <section aria-label="Expiry urgency">
            <h2 style={{ fontSize: 15 }}>Expiry urgency</h2>
            {Object.keys(EXPIRY_LABELS).map((bucket) => (
              <CountRow
                key={bucket}
                label={EXPIRY_LABELS[bucket]}
                value={data.expiry[bucket] ?? 0}
              />
            ))}
          </section>
          <section aria-label="Categories">
            <h2 style={{ fontSize: 15 }}>Categories</h2>
            {data.categories.taxonomy.map((category) => (
              <CountRow
                key={category.id}
                label={category.name}
                value={data.categories.counts[category.id] ?? 0}
              />
            ))}
            <CountRow label="Uncategorized" value={data.categories.uncategorized} />
          </section>
          <section aria-label="Signals">
            <h2 style={{ fontSize: 15 }}>Signals</h2>
            <CountRow
              label="Expired still active"
              value={data.waste.expired_untouched}
            />
            <CountRow
              label="Suggestions pending"
              value={data.adherence.suggestions.pending ?? 0}
            />
            <CountRow
              label="Suggestions confirmed"
              value={data.adherence.suggestions.confirmed ?? 0}
            />
            <CountRow
              label="Review tasks open"
              value={data.adherence.review_tasks.open ?? 0}
            />
          </section>
        </div>
      )}

      <div style={{ marginTop: 20 }}>
        <button
          type="button"
          onClick={() => insights.mutate()}
          disabled={!effectiveHousehold || insights.isPending}
        >
          {insights.isPending ? "Generating…" : "Generate summary"}
        </button>
      </div>
      {message && (
        <div role="alert" style={{ marginTop: 12, color: "#374151" }}>
          {message}
        </div>
      )}

      {insightResult?.status === "ok" && insightResult.summary && (
        <section aria-label="Generated summary" style={{ marginTop: 20 }}>
          <h2 style={{ fontSize: 15 }}>Summary</h2>
          <p>{insightResult.summary}</p>
          {insightResult.cited_stats && insightResult.cited_stats.length > 0 && (
            <div>
              <h3 style={{ fontSize: 13, color: "#6b7280" }}>Grounded in</h3>
              <ul>
                {insightResult.cited_stats.map((stat) => (
                  <li key={stat.id}>
                    {stat.label}: {String(stat.value)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
