import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { clearOpenedDate, fetchOpenedCountdown, recordOpenedDate } from "../api/client";
import type { OpenedCountdownResponse, OpenedCountdownRow } from "../api/types";
import { CONTROL_STYLE, THEMED_CONTROL_CLASS } from "./shell/CatalogToolbar";

function daysText(days: number | null): string | null {
  if (days === null) return null;
  if (days < 0) {
    const past = Math.abs(days);
    return `Window passed ${past} ${past === 1 ? "day" : "days"} ago`;
  }
  if (days === 0) return "Window ends today";
  return `${days} ${days === 1 ? "day" : "days"} left`;
}

function windowText(row: OpenedCountdownRow): string {
  if (row.window_months === null) return "No window declared";
  return `${row.window_months}-month ${row.window_source === "category_default" ? "default" : row.window_source}`;
}

function OpenedRow({
  row,
  householdId,
  onSaved,
}: {
  row: OpenedCountdownRow;
  householdId: string;
  onSaved: () => void;
}) {
  const [value, setValue] = useState("");
  const [saving, setSaving] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const name = row.display_name || "Untitled item";

  const save = async () => {
    if (!value) return;
    setSaving(true);
    setError(null);
    try {
      await recordOpenedDate(row.asset_id, householdId, value);
      setEditing(false);
      onSaved();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setSaving(false);
    }
  };

  const clear = async () => {
    setClearing(true);
    setError(null);
    try {
      await clearOpenedDate(row.asset_id, householdId);
      setEditing(false);
      setValue("");
      onSaved();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setClearing(false);
    }
  };

  return (
    <div
      className="bg-card border-border"
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: 12,
        alignItems: "center",
        padding: 12,
        borderStyle: "solid",
        borderWidth: 1,
        borderRadius: 8,
      }}
    >
      <Link
        className="text-link focus-ring"
        style={{ textDecoration: "underline", fontWeight: 600 }}
        to={`/assets/${row.asset_id}?household_id=${householdId}`}
      >
        {name}
      </Link>
      {row.opened_date === null ? (
        <>
          <span className="text-muted-foreground" style={{ fontSize: 12 }}>No opened date yet</span>
          <input
            type="date"
            aria-label={`Opened date for ${name}`}
            className={THEMED_CONTROL_CLASS}
            style={CONTROL_STYLE}
            value={value}
            onChange={(event) => setValue(event.target.value)}
          />
          <button
            type="button"
            aria-label={`Save opened date for ${name}`}
            className={THEMED_CONTROL_CLASS}
            style={CONTROL_STYLE}
            disabled={!value || saving}
            onClick={() => void save()}
          >
            Save
          </button>
        </>
      ) : (
        <>
          <span className="text-muted-foreground" style={{ fontSize: 12 }}>Opened {row.opened_date}</span>
          <span style={{ fontSize: 13 }}>
            {row.days_open} {row.days_open === 1 ? "day" : "days"} open
          </span>
          <span className="text-muted-foreground" style={{ fontSize: 13 }}>{daysText(row.days_remaining)}</span>
          {editing ? (
            <>
              <input
                type="date"
                aria-label={`Opened date for ${name}`}
                className={THEMED_CONTROL_CLASS}
                style={CONTROL_STYLE}
                value={value}
                onChange={(event) => setValue(event.target.value)}
              />
              <button
                type="button"
                aria-label={`Save opened date for ${name}`}
                className={THEMED_CONTROL_CLASS}
                style={CONTROL_STYLE}
                disabled={!value || saving || clearing}
                onClick={() => void save()}
              >
                Save
              </button>
            </>
          ) : (
            <button
              type="button"
              aria-label={`Edit opened date for ${name}`}
              className={THEMED_CONTROL_CLASS}
              style={CONTROL_STYLE}
              disabled={clearing}
              onClick={() => {
                setValue(row.opened_date ?? "");
                setEditing(true);
              }}
            >
              Edit
            </button>
          )}
          <button
            type="button"
            aria-label={`Clear opened date for ${name}`}
            className={THEMED_CONTROL_CLASS}
            style={CONTROL_STYLE}
            disabled={saving || clearing}
            onClick={() => void clear()}
          >
            Clear
          </button>
        </>
      )}
      <span
        data-testid="opened-window"
        className="bg-card-muted"
        style={{ marginLeft: "auto", padding: "2px 8px", borderRadius: 999, fontSize: 12 }}
      >
        {windowText(row)}
      </span>
      {error && (
        <div role="alert" className="text-danger" style={{ flexBasis: "100%", fontSize: 12 }}>
          {error}
        </div>
      )}
    </div>
  );
}

export function OpenedCountdownSection({ householdId }: { householdId: string }) {
  const queryClient = useQueryClient();
  const query = useQuery<OpenedCountdownResponse>({
    queryKey: ["opened-countdown", householdId],
    queryFn: () => fetchOpenedCountdown(householdId),
    enabled: !!householdId,
  });
  const rows = query.data?.rows ?? [];

  return (
    <section aria-label="Opened countdown" style={{ marginTop: 20 }}>
      <h2 style={{ fontSize: 15 }}>Opened countdown</h2>
      <p className="text-muted-foreground" style={{ fontSize: 13 }}>
        Days since each cosmetics item was opened, counted against its category&apos;s
        after-opening window.
      </p>
      {query.isLoading && <div>Loading opened countdown…</div>}
      {query.isError && (
        <div role="alert" className="text-danger" style={{ fontSize: 12 }}>
          {String(query.error)}
        </div>
      )}
      {query.data && rows.length === 0 && (
        <div role="status" className="text-muted-foreground" style={{ fontSize: 12 }}>
          No cosmetics items to track.
        </div>
      )}
      {rows.length > 0 && (
        <div style={{ display: "grid", gap: 8 }}>
          {rows.map((row) => (
            <OpenedRow
              key={row.asset_id}
              row={row}
              householdId={householdId}
              onSaved={() => {
                void queryClient.invalidateQueries({
                  queryKey: ["opened-countdown", householdId],
                });
              }}
            />
          ))}
        </div>
      )}
    </section>
  );
}
