import { useState, type ReactNode } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  dismissReminder,
  fetchAnalyticsSummary,
  fetchExpiryStatus,
  fetchReminders,
  markReminderRead,
} from "../api/client";
import type {
  AnalyticsSummary,
  ExpiryStatusResponse,
  ReminderListResponse,
} from "../api/types";
import { DATE_TYPE_LABELS } from "../components/ExpiryEntryForm";
import { OpenedCountdownSection } from "../components/OpenedCountdownSection";
import { CONTROL_STYLE, THEMED_CONTROL_CLASS } from "../components/shell/CatalogToolbar";
import { PageContainer } from "../components/shell/PageContainer";
import { useTaxonomy } from "../hooks/useAssets";
import { useHouseholdContext } from "../hooks/HouseholdContext";

// Blueprint §11.2 screen 7: the fixed urgency buckets, in that order.
const BUCKET_SECTIONS: { bucket: string; label: string }[] = [
  { bucket: "expired", label: "Expired" },
  { bucket: "this-week", label: "This week" },
  { bucket: "this-month", label: "This month" },
  { bucket: "safe", label: "Safe" },
];

// The engine's tier names, labelled for display. A null tier is its own label.
const TIER_LABELS: Record<string, string> = {
  critical: "Use first",
  urgent: "Use soon",
  upcoming: "Upcoming",
  long_lead: "Long lead",
  safe: "Safe",
};

const REASON_LABELS: Record<string, string> = {
  proposed: "Date proposed",
  needs_evidence: "Needs evidence",
  unparseable: "Unparseable date",
  dateless: "No date",
};

function tierLabel(tier: string | null): string {
  if (!tier) return "";
  if (TIER_LABELS[tier]) return TIER_LABELS[tier];
  return tier.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function daysLabel(days: number): string {
  if (days < 0) {
    const overdue = Math.abs(days);
    return `${overdue} ${overdue === 1 ? "day" : "days"} overdue`;
  }
  if (days === 0) return "Due today";
  return `${days} ${days === 1 ? "day" : "days"} remaining`;
}

type ExpiryRowItem = {
  asset_id: string;
  display_name: string | null;
  days_remaining: number;
  tier: string | null;
};

function ExpiryRow({ row, householdId, detail }: { row: ExpiryRowItem; householdId: string; detail: ReactNode }) {
  return (
    <div
      style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center", padding: 12, backgroundColor: "hsl(var(--paper))", color: "hsl(var(--ink))", borderStyle: "solid", borderWidth: 1, borderColor: "hsl(var(--line))", borderRadius: 0 }}
    >
      <Link
        className="text-link focus-ring"
        style={{ textDecoration: "underline", fontWeight: 600 }}
        to={`/assets/${row.asset_id}?household_id=${householdId}`}
      >
        {row.display_name || "Untitled item"}
      </Link>
      {detail}
      <span style={{ fontSize: 13, color: "hsl(var(--ink-muted))" }}>{daysLabel(row.days_remaining)}</span>
      {row.tier ? (
        <span data-testid="tier-pill" style={{ fontSize: 13, color: "hsl(var(--ink-muted))" }}>
          {tierLabel(row.tier)}
        </span>
      ) : null}
    </div>
  );
}

export function ExpiryPage() {
  // SG-196 G1: household selection comes from the shared context.
  const { households, householdId } = useHouseholdContext();
  const { data: taxonomy } = useTaxonomy();
  const queryClient = useQueryClient();
  const [category, setCategory] = useState("");
  const [pendingReminder, setPendingReminder] = useState<{ id: string; action: "read" | "dismiss" } | null>(null);
  const [reminderError, setReminderError] = useState<string | null>(null);
  const effectiveHousehold = householdId || households?.[0]?.id || "";

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
  const reminders = useQuery<ReminderListResponse>({
    queryKey: ["reminders", effectiveHousehold],
    queryFn: () => fetchReminders(effectiveHousehold),
    enabled: !!effectiveHousehold,
  });

  const categories = taxonomy?.plugins.find((plugin) => plugin.plugin_id === "expiry-tracker")?.categories ?? [];
  const categoryName = (slug: string) => categories.find((entry) => entry.id === slug)?.name ?? "Other";

  const data = status.data;
  const rows = data?.rows ?? [];
  const unresolved = data?.unresolved_rows ?? [];
  const isEmpty = !!data && rows.length === 0 && unresolved.length === 0;
  const unreadReminders = (reminders.data?.items ?? []).filter((item) => item.status === "unread");
  const unreadCount = reminders.data?.unread_count ?? 0;

  // SG-235: the server owns the unread count and the row list. A transition
  // re-reads the same query key; nothing is removed or decremented locally.
  const transitionReminder = async (reminderId: string, action: "read" | "dismiss") => {
    setPendingReminder({ id: reminderId, action });
    setReminderError(null);
    try {
      if (action === "read") {
        await markReminderRead(reminderId, effectiveHousehold);
      } else {
        await dismissReminder(reminderId, effectiveHousehold);
      }
      await queryClient.invalidateQueries({ queryKey: ["reminders", effectiveHousehold] });
    } catch (error) {
      setReminderError(error instanceof Error ? error.message : String(error));
    } finally {
      setPendingReminder(null);
    }
  };

  return (
    <PageContainer className="text-foreground">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <h1 className="page-header text-foreground">Expiry</h1>
        <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <label style={{ fontSize: 13 }}>
            Shelf life filter{" "}
            <select
              aria-label="Shelf life filter"
              className={THEMED_CONTROL_CLASS}
              style={{ ...CONTROL_STYLE, borderRadius: 0 }}
              value={category}
              onChange={(event) => setCategory(event.target.value)}
            >
              <option value="">All categories</option>
              {categories.map((entry) => (
                <option key={entry.id} value={entry.id}>{entry.name}</option>
              ))}
            </select>
          </label>
        </div>
      </div>
      <p style={{ fontSize: 13, color: "hsl(var(--ink-muted))" }}>
        Food and other dated things, soonest first.
      </p>

      <div style={{ marginTop: 20 }}>
        <h2 style={{ fontSize: 15 }}>Unread reminders ({unreadCount})</h2>
        {unreadReminders.length === 0 ? (
          <div className="text-muted-foreground" style={{ fontSize: 13 }}>None</div>
        ) : (
          <div style={{ display: "grid", gap: 8 }}>
            {unreadReminders.map((reminder) => (
              <ExpiryRow
                key={reminder.id}
                row={reminder}
                householdId={effectiveHousehold}
                detail={
                  <>
                    <span style={{ fontSize: 13, color: "hsl(var(--ink-muted))" }}>
                      Checked {reminder.as_of_day}
                    </span>
                    <div style={{ display: "flex", gap: 8 }}>
                      <button
                        type="button"
                        aria-label="Mark reminder read"
                        className={THEMED_CONTROL_CLASS}
                        style={{ ...CONTROL_STYLE, borderRadius: 0 }}
                        disabled={pendingReminder?.id === reminder.id}
                        onClick={() => void transitionReminder(reminder.id, "read")}
                      >
                        Read
                      </button>
                      <button
                        type="button"
                        aria-label="Dismiss reminder"
                        className={THEMED_CONTROL_CLASS}
                        style={{ ...CONTROL_STYLE, borderRadius: 0 }}
                        disabled={pendingReminder?.id === reminder.id}
                        onClick={() => void transitionReminder(reminder.id, "dismiss")}
                      >
                        Dismiss
                      </button>
                    </div>
                  </>
                }
              />
            ))}
          </div>
        )}
        {reminderError && (
          <div role="alert" className="text-danger" style={{ marginTop: 8, fontSize: 13 }}>
            {reminderError}
          </div>
        )}
      </div>

      <OpenedCountdownSection householdId={effectiveHousehold} />

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
                  <div className="text-muted-foreground" style={{ fontSize: 13 }}>None</div>
                ) : (
                  <div style={{ display: "grid", gap: 8 }}>
                    {sectionRows.map((row) => (
                      <ExpiryRow
                        key={row.asset_id}
                        row={row}
                        householdId={effectiveHousehold}
                        detail={
                          <>
                            <span className="text-muted-foreground" style={{ fontSize: 13 }}>{categoryName(row.category)}</span>
                            <span style={{ fontSize: 13 }}>
                              {row.expiry_date}
                              {row.date_type ? ` · ${DATE_TYPE_LABELS[row.date_type] ?? "Date"}` : ""}
                            </span>
                          </>
                        }
                      />
                    ))}
                  </div>
                )}
              </section>
            );
          })}

          <section aria-label="Unresolved" style={{ marginTop: 20 }}>
            <h2 style={{ fontSize: 15 }}>Unresolved ({unresolved.length})</h2>
            {(data.summary.dateless ?? 0) > 0 && (
              <div role="status" className="text-muted-foreground" style={{ fontSize: 13, marginBottom: 6 }}>
                {data.summary.dateless} {data.summary.dateless === 1 ? "item is" : "items are"} set to need no date — nothing to do here.
              </div>
            )}
            {unresolved.length === 0 ? (
              <div className="text-muted-foreground" style={{ fontSize: 13 }}>None</div>
            ) : (
              <ul style={{ margin: 0, paddingLeft: 18 }}>
                {unresolved.map((row) => (
                    <li key={row.asset_id}>
                      <Link
                        className="text-link focus-ring"
                        to={`/assets/${row.asset_id}?household_id=${effectiveHousehold}`}
                      >
                        {REASON_LABELS[row.reason] ?? "Needs a date"}
                        {" · Unnamed item"}
                      </Link>
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
            <span>Items without a shelf life</span>
            <strong>{summary.data.categories.uncategorized}</strong>
          </div>
        </section>
      )}
    </PageContainer>
  );
}
