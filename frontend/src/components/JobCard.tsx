import type { Job } from "../api/types";

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

export function JobCard({ job, selected, onSelect }: { job: Job; selected: boolean; onSelect: () => void }) {
  return (
    <button
      type="button"
      onClick={onSelect}
      aria-pressed={selected}
      className={`bg-card text-foreground ${selected ? "border-primary" : "border-border"} focus-ring`}
      style={{
        display: "block", width: "100%", textAlign: "left", padding: 14, borderRadius: 8,
        borderStyle: "solid", borderWidth: selected ? 2 : 1, cursor: "pointer",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
        <strong>Import {job.id.slice(0, 8)}</strong>
        <span data-testid={`job-state-${job.id}`} className={jobStateTone(job.state)}>{job.state}</span>
      </div>
      <div className="text-muted-foreground" style={{ fontSize: 12, marginTop: 6 }}>{job.job_type} · {job.created_at || ""}</div>
      {job.progress && <div style={{ fontSize: 12, marginTop: 8 }}>Progress: {job.progress.completed}/{job.progress.total} complete · {job.progress.failed} failed · {job.progress.pending} pending</div>}
    </button>
  );
}
