import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { apiGet, candidateDecision, candidateSplit } from "../api/client";
import type { Candidate, CandidateSplitChild, ReviewTaskListResponse } from "../api/types";
import { CandidateCard } from "../components/CandidateCard";
import { ExpiryEntryForm } from "../components/ExpiryEntryForm";

function splitChildLabel(child: CandidateSplitChild): string {
  const raw = child.fields.display_name;
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    const value = (raw as Record<string, unknown>).value;
    if (value != null) return String(value);
  }
  if (raw != null) return String(raw);
  return child.id;
}

function multiItemCount(task: { proposed_change: unknown } | undefined): number | null {
  const change = task?.proposed_change;
  if (change && typeof change === "object" && !Array.isArray(change)) {
    const count = (change as Record<string, unknown>).item_count;
    if (typeof count === "number" && Number.isInteger(count) && count >= 2) return count;
  }
  return null;
}

export function ReviewPage() {
  const { candidateId = "" } = useParams();
  const [search] = useSearchParams();
  const householdId = search.get("household_id") || localStorage.getItem("household_id") || "";
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [assetId, setAssetId] = useState<string | null>(null);
  const [keyboardAction, setKeyboardAction] = useState("");
  const [splitChildren, setSplitChildren] = useState<CandidateSplitChild[]>([]);
  const candidateQuery = useQuery<Candidate>({ queryKey: ["candidate", candidateId, householdId], queryFn: () => apiGet<Candidate>(`/v1/candidates/${candidateId}`, { household_id: householdId }), enabled: !!candidateId && !!householdId });
  const tasksQuery = useQuery<ReviewTaskListResponse>({ queryKey: ["review-tasks", householdId], queryFn: () => apiGet<ReviewTaskListResponse>("/v1/review-tasks", { household_id: householdId }), enabled: !!householdId });
  useEffect(() => { if (candidateQuery.data?.asset_id) setAssetId(candidateQuery.data.asset_id); }, [candidateQuery.data?.asset_id]);
  const decision = useMutation({ mutationFn: ({ action, fields }: { action: "accept" | "edit" | "hold" | "reject"; fields?: Record<string, unknown> }) => candidateDecision(candidateId, householdId, action, fields), onSuccess: (result) => { if (result.asset_id) setAssetId(result.asset_id); qc.invalidateQueries({ queryKey: ["candidate", candidateId, householdId] }); } });
  const splitItemCount = multiItemCount((tasksQuery.data?.items ?? []).find((task) => task.subject_ref === candidateId && task.task_type === "candidate.multi_item" && task.status === "open"));
  const split = useMutation({ mutationFn: (indexes: number[]) => candidateSplit(candidateId, householdId, indexes), onSuccess: (result) => { setSplitChildren(result.children); qc.invalidateQueries({ queryKey: ["candidate", candidateId, householdId] }); qc.invalidateQueries({ queryKey: ["review-tasks", householdId] }); } });
  const candidate = candidateQuery.data;
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if ((event.target as HTMLElement)?.tagName === "INPUT" || (event.target as HTMLElement)?.tagName === "TEXTAREA") return;
      if (event.key.toLowerCase() === "a" && candidate && candidate.review_task_ids.length === 0) { event.preventDefault(); setKeyboardAction("accept"); decision.mutate({ action: "accept", fields: candidate.fields as Record<string, unknown> }); }
      if (event.key.toLowerCase() === "r" && candidate) { event.preventDefault(); setKeyboardAction("reject"); decision.mutate({ action: "reject" }); }
      if (event.key === "ArrowLeft") { event.preventDefault(); setKeyboardAction("previous"); navigate(-1); }
      if (event.key === "ArrowRight") { event.preventDefault(); setKeyboardAction("next"); navigate(1); }
    }
    window.addEventListener("keydown", onKey); return () => window.removeEventListener("keydown", onKey);
  }, [candidate, decision, navigate]);

  return <div className="text-foreground" style={{ padding: 24, maxWidth: 1100 }}><Link to={`/inbox?household_id=${householdId}`} className="text-primary focus-ring">← Back to inbox</Link><h1 className="page-header text-foreground">Review workspace</h1>{candidateQuery.isLoading && <div>Loading candidate…</div>}{candidateQuery.error && <div role="alert">{candidateQuery.error.message}</div>}{candidate && <><CandidateCard candidate={candidate} householdId={householdId} busy={decision.isPending} onDecision={(action, fields) => decision.mutate({ action, fields })} splitItemCount={splitItemCount} onSplit={() => { if (splitItemCount != null) split.mutate(Array.from({ length: splitItemCount }, (_, index) => index)); }} splitBusy={split.isPending} />{decision.error && <div role="alert" style={{ marginTop: 10 }}>{decision.error.message}</div>}{split.error && <div role="alert" style={{ marginTop: 10 }}>{split.error.message}</div>}{splitChildren.length > 0 && <section aria-label="Split candidates" style={{ marginTop: 16 }}><h2>Split into {splitChildren.length} items</h2><ul>{splitChildren.map((child) => <li key={child.id}><Link to={`/review/${child.id}?household_id=${householdId}`}>{splitChildLabel(child)}</Link></li>)}</ul></section>}{keyboardAction && <div role="status" data-testid="keyboard-action">Keyboard: {keyboardAction}</div>}{assetId && <ExpiryEntryForm assetId={assetId} householdId={householdId} evidenceIds={candidate.evidence_ids} />}</>}</div>;
}
