import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { fetchAnalyticsSummary, fetchExpiryStatus } from "../api/client";
import type {
  AnalyticsSummary,
  ExpiryStatusResponse,
  ExpiryStatusRow,
  Household,
} from "../api/types";
import { CONTROL_STYLE, THEMED_CONTROL_CLASS } from "../components/shell/CatalogToolbar";
import { PageContainer } from "../components/shell/PageContainer";
import { useHouseholds, useTaxonomy } from "../hooks/useAssets";

// Blueprint §11.2 screen 7: the fixed urgency buckets, in that order.
const BUCKET_SECTIONS: { bucket: string; label: string }[] = [
  { bucket: "expired", label: "Expired" },
  { bucket: "this-week", label: "This week" },
  { bucket: "this-month", label: "This month" },
  { bucket: "safe", label: "Safe" },
];

// The engine's tier names, labelled for display. A null tier is its own label.
const TIER_LABELS: Record<string, string> = {
  critical: "Critical",
  urgent: "Urgent",
  upcoming: "Upcoming",
  long_lead: "Long lead",
  safe: "Safe",
};

const REASON_LABELS: Record<string, string> = {
  proposed: "Proposed",
  needs_evidence: "Needs evidence",
  unparseable: "Unparseable date",
  dateless: "No date",
};

function tierLabel(tier: string | null): string {
  if (!tier) return "No tier";
  return TIER_LABELS[tier] ?? tier;
}

function daysLabel(days: number): string {
  if (days < 0) {
    const overdue = Math.abs(days);
    return `${overdue} ${overdue === 1 ? "day" : "days"} overdue`;
  }
  if (days === 0) return "Due today";
  return `${days} ${days === 1 ? "day" : "days"} remaining`;
}

function ExpiryRow({ row, householdId, categoryName }: { row: ExpiryStatusRow; householdId: string; categoryName: (slug: string) => string }) {
  return (
    <div
      className="bg-card border-border"
      style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center", padding: 12, borderStyle: "solid", borderWidth: 1, borderRadius: 8 }}
    >
      <Link
        className="text-primary focus-ring"
        style={{ textDecoration: "underline", fontWeight: 600 }}
        to={`/assets/${row.asset_id}?household_id=${householdId}`}
      >
        {row.display_name || "Untitled item"}
      </Link>
      <span className="text-muted-foreground" style={{ fontSize: 12 }}>{categoryName(row.category)}</span>
      <span style={{ fontSize: 13 }}>
        {row.expiry_date}
        {row.date_type ? ` · ${row.date_type}` : ""}
      </span>
      <span className="text-muted-foreground" style={{ fontSize: 13 }}>{daysLabel(row.days_remaining)}</span>
      <span
        data-testid="tier-pill"
        className="bg-card-muted"
        style={{ marginLeft: "auto", padding: "2px 8px", borderRadius: 999, fontSize: 12 }}
      >
        {tierLabel(row.tier)}
      </span>
    </div>
  );
}

export function ExpiryPage() {
  const { data: households } = useHouseholds();
  const { data: taxonomy } = useTaxonomy();
  const [householdId, setHouseholdId] = useState(() => localStorage.getItem("household_id") || "");
  const [category, setCategory] = useState("");
  const effectiveHousehold = householdId || households?.[0]?.id || "";

  useEffect(() => {
    if (!householdId && households?.[0]) {
      setHouseholdId(households[0].id);
      localStorage.setItem("household_id", households[0].id);
    }
  }, [householdId, households]);

  const status = useQuery<ExpiryStatusResponse>({
    queryKey: ["expiry-status", effectiveHousehold, category],
    queryFn: () => fetchExpiryStatus(effectiveHousehold, category || undefined),
    enabled: !!effectiveHousehold,
  });
  const summary = useQuery<AnalyticsSummary>({
    queryKey: ["analytics-summary", effectiveHousehold],
    queryFn: () => fetchAnalyticsSummary(effectiveHousehold),
    enabled: !!effectiveHousehold,
  });

  const categories = taxonomy?.plugins.find((plugin) => plugin.plugin_id === "expiry-tracker")?.categories ?? [];
  const categoryName = (slug: string) => categories.find((entry) => entry.id === slug)?.name ?? slug;

  const data = status.data;
  const rows = data?.rows ?? [];
  const unresolved = data?.unresolved_rows ?? [];
  const isEmpty = !!data && rows.length === 0 && unresolved.length === 0;

  return (
    <PageContainer className="text-foreground">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <h1 className="page-header text-foreground">Expiry</h1>
        <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <label style={{ fontSize: 13 }}>
            Category filter{" "}
            <select
              aria-label="Category filter"
              className={THEMED_CONTROL_CLASS}
              style={CONTROL_STYLE}
              value={category}
              onChange={(event) => setCategory(event.target.value)}
            >
              <option value="">All categories</option>
              {categories.map((entry) => (
                <option key={entry.id} value={entry.id}>{entry.name}</option>
              ))}
            </select>
          </label>
          <label style={{ fontSize: 13 }}>
            Household{" "}
            <select
              aria-label="Household"
              className={THEMED_CONTROL_CLASS}
              style={CONTROL_STYLE}
              value={effectiveHousehold}
              onChange={(event) => {
                setHouseholdId(event.target.value);
                localStorage.setItem("household_id", event.target.value);
              }}
            >
              <option value="">Select household</option>
              {(households as Household[] | undefined)?.map((entry) => (
                <option key={entry.id} value={entry.id}>{entry.name}</option>
              ))}
            </select>
          </label>
        </div>
      </div>
      <p className="text-muted-foreground" style={{ fontSize: 13 }}>
        Items are grouped by the accepted expiry date each one carries, in blueprint urgency order.
        Filtering a category narrows the read on the server; the uncategorized count below comes from
        the served analytics summary and is never merged into the expiry stream.
      </p>

      {status.isLoading && <div>Loading expiry status…</div>}
      {status.isError && (
        <div role="alert" className="text-danger" style={{ marginTop: 12 }}>{String(status.error)}</div>
      )}
      {isEmpty && <div role="status">No expiry items for this household.</div>}

      {data && !isEmpty && (
        <>
          {BUCKET_SECTIONS.map((section) => {
            const sectionRows = rows.filter((row) => row.bucket === section.bucket);
            return (
              <section key={section.bucket} aria-label={section.label} style={{ marginTop: 20 }}>
                <h2 style={{ fontSize: 15 }}>{section.label} ({sectionRows.length})</h2>
                {sectionRows.length === 0 ? (
                  <div className="text-muted-foreground" style={{ fontSize: 12 }}>None</div>
                ) : (
                  <div style={{ display: "grid", gap: 8 }}>
                    {sectionRows.map((row) => (
                      <ExpiryRow key={row.asset_id} row={row} householdId={effectiveHousehold} categoryName={categoryName} />
                    ))}
                  </div>
                )}
              </section>
            );
          })}

          <section aria-label="Unresolved" style={{ marginTop: 20 }}>
            <h2 style={{ fontSize: 15 }}>Unresolved ({unresolved.length})</h2>
            {unresolved.length === 0 ? (
              <div className="text-muted-foreground" style={{ fontSize: 12 }}>None</div>
            ) : (
              <ul style={{ margin: 0, paddingLeft: 18 }}>
                {unresolved.map((row) => (
                  <li key={row.asset_id}>
                    <Link className="text-primary focus-ring" to={`/assets/${row.asset_id}?household_id=${effectiveHousehold}`}>
                      {row.asset_id}
                    </Link>
                    {" · "}
                    <span>{REASON_LABELS[row.reason] ?? row.reason}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}

      {summary.data && (
        <section aria-label="Uncategorized" style={{ marginTop: 20 }}>
          <h2 style={{ fontSize: 15 }}>Uncategorized</h2>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
            <span>Items outside the expiry stream (no accepted classification)</span>
            <strong>{summary.data.categories.uncategorized}</strong>
          </div>
        </section>
      )}
    </PageContainer>
  );
}
