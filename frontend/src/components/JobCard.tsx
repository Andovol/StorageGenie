import type { Job } from "../api/types";
import { formatJobDate, labelJobState } from "../lib/labels";

/**
 * SG-105 G3: status toned by state. The tones reuse the existing semantic
 * tokens so the state reads on the dark card; unmapped states fall back to the
 * muted foreground rather than a browser default.
 */
export function jobStateTone(state: string): string {
  switch ((state ?? "").toUpperCase()) {
    case "FAILED":
    case "ERROR":
      return "text-danger";
    case "COMPLETED":
    case "SUCCEEDED":
      return "text-success";
    case "PROCESSING":
    case "RUNNING":
    case "IN_PROGRESS":
      return "text-processed";
    default:
      return "text-muted-foreground";
  }
}

function labelJobKind(jobType: string): string {
  if (jobType === "import") return "Import";
  if (jobType === "enrich") return "Enrich";
  return jobType.replace(/[_.]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

// SG-324 P6: a job is named by when it was made — "Import · 14 Nov, 19:30"
// (the shared formatJobDate form). Without a date it keeps "Import job".
export function jobDisplayName(job: Job): string {
  const kind = labelJobKind(job.job_type);
  const when = formatJobDate(job.created_at);
  if (!when) return `${kind} job`;
  return `${kind} · ${when}`;
}

// SG-324 P6: skipped steps are known from the job's steps — a step whose
// output status is "skipped" (the same shape labelStepStatus reads). The list
// read carries no steps, so the count is 0 there; the detail read does.
export function skippedStepCount(job: Job): number {
  const steps = job.steps ?? [];
  return steps.filter((step) => {
    const output = step.output as Record<string, unknown> | null;
    return !!output && typeof output === "object" && (output as Record<string, unknown>).status === "skipped";
  }).length;
}

// SG-324 P6: done and total exclude skipped steps — "4 of 4 steps done · 2
// skipped", plus failed/pending only when non-zero.
export function jobProgressText(job: Job): string | null {
  if (!job.progress) return null;
  const skipped = skippedStepCount(job);
  const done = Math.max(0, job.progress.completed - skipped);
  const denom = Math.max(0, job.progress.total - skipped);
  const parts = [`${done} of ${denom} steps done`];
  if (skipped > 0) parts.push(`${skipped} skipped`);
  if (job.progress.failed > 0) parts.push(`${job.progress.failed} failed`);
  if (job.progress.pending > 0) parts.push(`${job.progress.pending} pending`);
  return parts.join(" · ");
}

export function JobCard({ job, selected, onSelect }: { job: Job; selected: boolean; onSelect: () => void }) {
  const name = jobDisplayName(job);
  const progress = jobProgressText(job);
  return (
    <button
      type="button"
      onClick={onSelect}
      aria-pressed={selected}
      aria-label={`${name}, ${labelJobState(job.state)}`}
      className="focus-ring"
      style={{
        display: "block", width: "100%", textAlign: "left", padding: 14, borderRadius: 0,
        borderStyle: "solid", borderWidth: selected ? 2 : 1, cursor: "pointer",
        backgroundColor: "hsl(var(--paper))", color: "hsl(var(--ink))",
        borderColor: selected ? "hsl(var(--ink))" : "hsl(var(--line))",
        textDecoration: selected ? "underline" : "none",
        textUnderlineOffset: 3,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
        <strong>{name}</strong>
        <span className={jobStateTone(job.state)}>{labelJobState(job.state)}</span>
      </div>
      <div style={{ fontSize: 13, marginTop: 6, color: "hsl(var(--ink-muted))" }}>{formatJobDate(job.created_at)}</div>
      {progress && <div style={{ fontSize: 13, marginTop: 8 }}>{progress}</div>}
    </button>
  );
}
