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

export function JobCard({ job, selected, onSelect }: { job: Job; selected: boolean; onSelect: () => void }) {
  return (
    <button
      type="button"
      onClick={onSelect}
      aria-pressed={selected}
      aria-label={`${labelJobKind(job.job_type)} job, ${labelJobState(job.state)}`}
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
        <strong>{labelJobKind(job.job_type)} job</strong>
        <span className={jobStateTone(job.state)}>{labelJobState(job.state)}</span>
      </div>
      <div style={{ fontSize: 13, marginTop: 6, color: "hsl(var(--ink-muted))" }}>{formatJobDate(job.created_at)}</div>
      {job.progress && <div style={{ fontSize: 13, marginTop: 8 }}>Progress: {job.progress.completed}/{job.progress.total} complete · {job.progress.failed} failed · {job.progress.pending} pending</div>}
    </button>
  );
}
