import type { Job } from "../api/types";

export function JobCard({ job, selected, onSelect }: { job: Job; selected: boolean; onSelect: () => void }) {
  return (
    <button
      type="button"
      onClick={onSelect}
      aria-pressed={selected}
      className={`bg-card ${selected ? "border-primary" : "border-border"} focus-ring`}
      style={{
        display: "block", width: "100%", textAlign: "left", padding: 14, borderRadius: 8,
        borderStyle: "solid", borderWidth: selected ? 2 : 1, cursor: "pointer",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
        <strong>Import {job.id.slice(0, 8)}</strong>
        <span data-testid={`job-state-${job.id}`}>{job.state}</span>
      </div>
      <div className="text-muted-foreground" style={{ fontSize: 12, marginTop: 6 }}>{job.job_type} · {job.created_at || ""}</div>
      {job.progress && <div style={{ fontSize: 12, marginTop: 8 }}>Progress: {job.progress.completed}/{job.progress.total} complete · {job.progress.failed} failed · {job.progress.pending} pending</div>}
    </button>
  );
}
