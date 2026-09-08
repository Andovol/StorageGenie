import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { apiGet, apiPost, resolveReviewTask } from "../api/client";
import type { Household, Job, JobListResponse, ReviewTaskListResponse } from "../api/types";
import { JobCard } from "../components/JobCard";
import { useHouseholds } from "../hooks/useAssets";

export function InboxPage() {
  const { data: households } = useHouseholds();
  const [householdId, setHouseholdId] = useState(() => localStorage.getItem("household_id") || "");
  const [selectedJobId, setSelectedJobId] = useState("");
  const qc = useQueryClient();
  const effectiveHousehold = householdId || households?.[0]?.id || "";
  useEffect(() => { if (!householdId && households?.[0]) { setHouseholdId(households[0].id); localStorage.setItem("household_id", households[0].id); } }, [householdId, households]);
  const jobs = useQuery<JobListResponse>({ queryKey: ["jobs", effectiveHousehold], queryFn: () => apiGet<JobListResponse>("/v1/jobs", { household_id: effectiveHousehold }), enabled: !!effectiveHousehold });
  const tasks = useQuery<ReviewTaskListResponse>({ queryKey: ["review-tasks", effectiveHousehold], queryFn: () => apiGet<ReviewTaskListResponse>("/v1/review-tasks", { household_id: effectiveHousehold }), enabled: !!effectiveHousehold });
  const detail = useQuery<Job>({ queryKey: ["import", selectedJobId, effectiveHousehold], queryFn: () => apiGet<Job>(`/v1/imports/${selectedJobId}`, { household_id: effectiveHousehold }), enabled: !!selectedJobId && !!effectiveHousehold });
  const retry = useMutation({ mutationFn: (jobId: string) => apiPost<Job>(`/v1/imports/${jobId}/retry`, {}, { household_id: effectiveHousehold }), onSuccess: (_, jobId) => { qc.invalidateQueries({ queryKey: ["jobs", effectiveHousehold] }); qc.invalidateQueries({ queryKey: ["import", jobId, effectiveHousehold] }); } });
  const resolve = useMutation({ mutationFn: (taskId: string) => resolveReviewTask(taskId, effectiveHousehold), onSuccess: () => qc.invalidateQueries({ queryKey: ["review-tasks", effectiveHousehold] }) });

  return <div style={{ padding: 24, maxWidth: 1100 }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}><h1>Inbox</h1><label>Household <select value={effectiveHousehold} onChange={(event) => { setHouseholdId(event.target.value); localStorage.setItem("household_id", event.target.value); }}><option value="">Select household</option>{(households as Household[] | undefined)?.map((household) => <option key={household.id} value={household.id}>{household.name}</option>)}</select></label></div>
    <div style={{ display: "grid", gridTemplateColumns: "minmax(260px, .8fr) minmax(320px, 1.2fr)", gap: 20 }}>
      <section><h2>Import jobs</h2>{jobs.isLoading && <div>Loading jobs…</div>}{!jobs.isLoading && jobs.data?.items.length === 0 && <div role="status">No import jobs yet.</div>}<div style={{ display: "grid", gap: 8 }}>{jobs.data?.items.map((job) => <JobCard key={job.id} job={job} selected={selectedJobId === job.id} onSelect={() => setSelectedJobId(job.id)} />)}</div></section>
      <section><h2>Selected job</h2>{!selectedJobId && <div>Select a job to see progress and errors.</div>}{detail.isLoading && <div>Loading job detail…</div>}{detail.data && <div><div><strong>{detail.data.state}</strong> · {detail.data.progress?.completed || 0}/{detail.data.progress?.total || 0} complete · {detail.data.progress?.failed || 0} failed · {detail.data.progress?.pending || 0} pending</div>{detail.data.errors?.map((error) => <div key={error} role="alert" style={{ color: "#b91c1c", marginTop: 8 }}>{error}</div>)}{detail.data.steps?.map((step) => <div key={step.id} style={{ marginTop: 8, padding: 8, background: "#f9fafb" }}><strong>{step.step_name}</strong>: {step.state}{step.error && <div role="alert">{step.error}</div>}</div>)}{detail.data.state === "FAILED" && <button type="button" onClick={() => retry.mutate(detail.data!.id)} disabled={retry.isPending} style={{ marginTop: 12 }}>{retry.isPending ? "Retrying…" : "Retry failed job"}</button>}</div>}</section>
    </div>
    <section style={{ marginTop: 28 }}><h2>Review queue</h2>{!tasks.isLoading && tasks.data?.items.length === 0 && <div role="status">No review tasks.</div>}<div style={{ display: "grid", gap: 8 }}>{tasks.data?.items.map((task) => <div key={task.id} style={{ display: "flex", justifyContent: "space-between", gap: 12, padding: 12, border: "1px solid #e5e7eb", borderRadius: 8 }}><div><strong>{task.task_type}</strong> · {task.priority} · {task.status}<div style={{ fontSize: 12, color: "#6b7280" }}>Task {task.id} · candidate {task.subject_ref}</div></div><div style={{ display: "flex", gap: 8 }}>{task.subject_ref && <Link to={`/review/${task.subject_ref}?household_id=${effectiveHousehold}`}>Review</Link>}{task.status === "open" && <button type="button" onClick={() => resolve.mutate(task.id)} disabled={resolve.isPending}>Resolve</button>}</div></div>)}</div></section>
  </div>;
}
