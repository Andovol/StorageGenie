import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { apiGet, apiPost, resolveReviewTask } from "../api/client";
import type { Job, JobListResponse } from "../api/types";
import { HouseholdSelector } from "../components/HouseholdSelector";
import { JobCard } from "../components/JobCard";
import { CONTROL_STYLE, THEMED_CONTROL_CLASS } from "../components/shell/CatalogToolbar";
import { PageContainer } from "../components/shell/PageContainer";
import { useReviewTasks } from "../hooks/useAssets";
import { useHouseholdContext } from "../hooks/HouseholdContext";

export function InboxPage() {
  // SG-196 G1: household selection comes from the shared context.
  const { households, householdId, setHouseholdId } = useHouseholdContext();
  const [selectedJobId, setSelectedJobId] = useState("");
  // SG-105 G3: resolved work is hidden by default; the status filter is the
  // in-tree precedent (PlanningPage's status select).
  const [reviewFilter, setReviewFilter] = useState<"open" | "resolved" | "all">("open");
  const qc = useQueryClient();
  const effectiveHousehold = householdId || households?.[0]?.id || "";
  const jobs = useQuery<JobListResponse>({ queryKey: ["jobs", effectiveHousehold], queryFn: () => apiGet<JobListResponse>("/v1/jobs", { household_id: effectiveHousehold }), enabled: !!effectiveHousehold });
  // SG-196 G3: shared with the nav badge through the same query key.
  const tasks = useReviewTasks(effectiveHousehold);
  const detail = useQuery<Job>({ queryKey: ["import", selectedJobId, effectiveHousehold], queryFn: () => apiGet<Job>(`/v1/imports/${selectedJobId}`, { household_id: effectiveHousehold }), enabled: !!selectedJobId && !!effectiveHousehold });
  const retry = useMutation({ mutationFn: (jobId: string) => apiPost<Job>(`/v1/imports/${jobId}/retry`, {}, { household_id: effectiveHousehold }), onSuccess: (_, jobId) => { qc.invalidateQueries({ queryKey: ["jobs", effectiveHousehold] }); qc.invalidateQueries({ queryKey: ["import", jobId, effectiveHousehold] }); } });
  // SG-187 G1: the modal's help promises an unchecked import "waits in the
  // Inbox until you run it there" — this is that run control.
  const run = useMutation({ mutationFn: (jobId: string) => apiPost<Job>(`/v1/imports/${jobId}/run`, {}, { household_id: effectiveHousehold }), onSuccess: (_, jobId) => { qc.invalidateQueries({ queryKey: ["jobs", effectiveHousehold] }); qc.invalidateQueries({ queryKey: ["import", jobId, effectiveHousehold] }); } });
  const resolve = useMutation({ mutationFn: (taskId: string) => resolveReviewTask(taskId, effectiveHousehold), onSuccess: () => qc.invalidateQueries({ queryKey: ["review-tasks", effectiveHousehold] }) });

  const reviewTasks = (tasks.data?.items ?? []).filter((task) =>
    reviewFilter === "all" ? true : reviewFilter === "resolved" ? task.status === "resolved" : task.status !== "resolved"
  );
  const totalTasks = tasks.data?.items.length ?? 0;

  return <PageContainer className="text-foreground">
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}><h1 className="page-header text-foreground">Inbox</h1><HouseholdSelector value={effectiveHousehold} onChange={setHouseholdId} households={households} selectStyle={CONTROL_STYLE} selectClassName={THEMED_CONTROL_CLASS} /></div>
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(280px, 100%), 1fr))", gap: 20 }}>
      <section><h2>Import jobs</h2>{jobs.isError && <div role="alert">Could not load import jobs: {String(jobs.error)}</div>}{jobs.isLoading && <div>Loading jobs…</div>}{!jobs.isLoading && jobs.data?.items.length === 0 && <div role="status">No import jobs yet.</div>}<div style={{ display: "grid", gap: 8 }}>{jobs.data?.items.map((job) => <JobCard key={job.id} job={job} selected={selectedJobId === job.id} onSelect={() => setSelectedJobId(job.id)} />)}</div></section>
      <section><h2>Selected job</h2>{!selectedJobId && <div>Select a job to see progress and errors.</div>}{detail.isError && <div role="alert">Could not load job detail: {String(detail.error)}</div>}{detail.isLoading && <div>Loading job detail…</div>}{detail.data && <div><div><strong>{detail.data.state}</strong> · {detail.data.progress?.completed || 0}/{detail.data.progress?.total || 0} complete · {detail.data.progress?.failed || 0} failed · {detail.data.progress?.pending || 0} pending</div>{detail.data.errors?.map((error) => <div key={error} role="alert" className="text-danger" style={{ marginTop: 8 }}>{error}</div>)}{detail.data.steps?.map((step) => <div key={step.id} className="bg-card-muted" style={{ marginTop: 8, padding: 8 }}><strong>{step.step_name}</strong>: {step.state}{step.error && <div role="alert">{step.error}</div>}</div>)}{detail.data.state === "CREATED" && <button type="button" onClick={() => run.mutate(detail.data!.id)} disabled={run.isPending} className={THEMED_CONTROL_CLASS} style={{ ...CONTROL_STYLE, marginTop: 12 }}>{run.isPending ? "Starting…" : "Start import job"}</button>}{detail.data.state === "FAILED" && <button type="button" onClick={() => retry.mutate(detail.data!.id)} disabled={retry.isPending} className={THEMED_CONTROL_CLASS} style={{ ...CONTROL_STYLE, marginTop: 12 }}>{retry.isPending ? "Retrying…" : "Retry failed job"}</button>}</div>}</section>
    </div>
    <section style={{ marginTop: 28 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <h2>Review queue</h2>
        <label style={{ fontSize: 13 }}>Review status <select aria-label="Review status" className={THEMED_CONTROL_CLASS} style={CONTROL_STYLE} value={reviewFilter} onChange={(event) => setReviewFilter(event.target.value as "open" | "resolved" | "all")}><option value="open">Open</option><option value="resolved">Resolved</option><option value="all">All</option></select></label>
      </div>
      {tasks.isError && <div role="alert">Could not load review tasks: {String(tasks.error)}</div>}
      {!tasks.isLoading && totalTasks === 0 && <div role="status">No review tasks.</div>}
      {!tasks.isLoading && totalTasks > 0 && reviewTasks.length === 0 && <div role="status">No {reviewFilter} review tasks.</div>}
      <div style={{ display: "grid", gap: 8 }}>{reviewTasks.map((task) => <div key={task.id} className="bg-card border-border" style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", gap: 12, padding: 12, borderStyle: "solid", borderWidth: 1, borderRadius: 8 }}><div><strong>{task.task_type}</strong> · {task.priority} · {task.status}<div className="text-muted-foreground" style={{ fontSize: 12 }}>Task {task.id} · candidate {task.subject_ref}</div></div><div style={{ display: "flex", gap: 8, alignItems: "center" }}>{task.subject_ref && <Link className="text-link focus-ring" style={{ textDecoration: "underline" }} to={`/review/${task.subject_ref}?household_id=${effectiveHousehold}`}>Review</Link>}{task.status === "open" && <button type="button" onClick={() => resolve.mutate(task.id)} disabled={resolve.isPending} className={THEMED_CONTROL_CLASS} style={CONTROL_STYLE}>Resolve</button>}</div></div>)}</div>
    </section>
  </PageContainer>;
}
