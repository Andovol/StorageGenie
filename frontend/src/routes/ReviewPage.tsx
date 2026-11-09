import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { apiGet, candidateDecision, candidateSplit, classifyAsset } from "../api/client";
import type { Candidate, CandidateSplitChild } from "../api/types";
import { CandidateCard } from "../components/CandidateCard";
import { CONTROL_STYLE, THEMED_CONTROL_CLASS } from "../components/shell/CatalogToolbar";
import { PageContainer } from "../components/shell/PageContainer";
import { useReviewTasks } from "../hooks/useAssets";

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

function fieldValue(raw: unknown): unknown {
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    const value = (raw as Record<string, unknown>).value;
    if (value !== undefined) return value;
  }
  return raw;
}

export function ReviewPage() {
  const { candidateId = "" } = useParams();
  const [search] = useSearchParams();
  const householdId = search.get("household_id") || localStorage.getItem("household_id") || "";
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [keyboardAction, setKeyboardAction] = useState("");
  const [splitChildren, setSplitChildren] = useState<CandidateSplitChild[]>([]);
  const [decisionAsset, setDecisionAsset] = useState<{ assetId: string; duplicate: boolean } | null>(null);
  // SG-271 G3 (F5/F12): the fresh accept's suggestion confirm state.
  const [confirmMessage, setConfirmMessage] = useState<string | null>(null);
  const [confirmError, setConfirmError] = useState<string | null>(null);
  const candidateQuery = useQuery<Candidate>({ queryKey: ["candidate", candidateId, householdId], queryFn: () => apiGet<Candidate>(`/v1/candidates/${candidateId}`, { household_id: householdId }), enabled: !!candidateId && !!householdId });
  // SG-198 G1: the review-tasks query is now the shared useReviewTasks
  // definition — same key, same queryFn, same enabled flag; the invalidation
  // below is unchanged.
  const tasksQuery = useReviewTasks(householdId);
  const decision = useMutation({ mutationFn: ({ action, fields }: { action: "accept" | "edit" | "hold" | "reject"; fields?: Record<string, unknown> }) => candidateDecision(candidateId, householdId, action, fields), onSuccess: (result) => { qc.invalidateQueries({ queryKey: ["candidate", candidateId, householdId] }); qc.invalidateQueries({ queryKey: ["review-tasks", householdId] }); setConfirmMessage(null); setConfirmError(null); if (result.asset_id) setDecisionAsset({ assetId: result.asset_id, duplicate: result.status === "duplicate_linked" }); } });
  const splitItemCount = multiItemCount((tasksQuery.data?.items ?? []).find((task) => task.subject_ref === candidateId && task.task_type === "candidate.multi_item" && task.status === "open"));
  const split = useMutation({ mutationFn: (indexes: number[]) => candidateSplit(candidateId, householdId, indexes), onSuccess: (result) => { setSplitChildren(result.children); qc.invalidateQueries({ queryKey: ["candidate", candidateId, householdId] }); qc.invalidateQueries({ queryKey: ["review-tasks", householdId] }); } });
  const candidate = candidateQuery.data;
  // SG-271 G3: the AI's shelf-life suggestion, shown after a fresh accept of a
  // new item. Confirm classifies the new item; nothing classifies without it.
  const proposedCategory = candidate ? fieldValue(candidate.fields.category_proposed) : null;
  const showSuggestion =
    decisionAsset !== null &&
    !decisionAsset.duplicate &&
    typeof proposedCategory === "string" &&
    proposedCategory.trim() !== "";
  const confirm = useMutation({
    mutationFn: () => classifyAsset(decisionAsset!.assetId, householdId, String(proposedCategory)),
    onSuccess: () => {
      setConfirmMessage("Shelf life saved — see it on the item page.");
      setConfirmError(null);
      qc.invalidateQueries({ queryKey: ["asset", decisionAsset!.assetId, householdId] });
    },
    onError: (caught: unknown) => {
      const text = caught instanceof Error ? caught.message : String(caught);
      setConfirmError(`${text} Pick the shelf life on the item page instead.`);
      setConfirmMessage(null);
    },
  });
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if ((event.target as HTMLElement)?.tagName === "INPUT" || (event.target as HTMLElement)?.tagName === "TEXTAREA") return;
      // SG-271 G2: a committed candidate offers no decision, by button or key.
      if (event.key.toLowerCase() === "a" && candidate && !candidate.asset_id && candidate.blocking_review_task_ids.length === 0 && !decision.isPending) { event.preventDefault(); setKeyboardAction("accept"); decision.mutate({ action: "accept", fields: candidate.fields as Record<string, unknown> }); }
      if (event.key.toLowerCase() === "r" && candidate && !candidate.asset_id && !decision.isPending) { event.preventDefault(); setKeyboardAction("reject"); decision.mutate({ action: "reject" }); }
      if (event.key === "ArrowLeft") { event.preventDefault(); setKeyboardAction("previous"); navigate(-1); }
      if (event.key === "ArrowRight") { event.preventDefault(); setKeyboardAction("next"); navigate(1); }
    }
    window.addEventListener("keydown", onKey); return () => window.removeEventListener("keydown", onKey);
  }, [candidate, decision, navigate]);

  return <PageContainer className="text-foreground"><Link to={`/inbox?household_id=${householdId}`} className="text-link focus-ring">← Back to inbox</Link><h1 className="page-header text-foreground">Review workspace</h1>{candidateQuery.isLoading && <div>Loading candidate…</div>}{candidateQuery.error && <div role="alert">{candidateQuery.error.message}</div>}{candidate && candidate.asset_id ? <section aria-label="Catalog item" className="bg-card border-border" style={{ borderStyle: "solid", borderWidth: 1, borderRadius: 10, padding: 16 }}><div role="status" style={{ fontWeight: 600 }}>In your catalog</div><div className="text-muted-foreground" style={{ fontSize: 13, marginTop: 4 }}>This suggestion is already an item. Decisions are finished — nothing left to accept or edit here.</div><div style={{ marginTop: 10 }}><Link className="text-link focus-ring" to={`/assets/${candidate.asset_id}?household_id=${householdId}`}>Open item</Link></div>{showSuggestion && decisionAsset && <div style={{ marginTop: 12, paddingTop: 12 }}><div>The AI suggests <strong>{String(proposedCategory)}</strong> as the shelf life.</div><div style={{ marginTop: 10 }}><button type="button" onClick={() => confirm.mutate()} disabled={confirm.isPending || confirmMessage !== null} className={THEMED_CONTROL_CLASS} style={{ ...CONTROL_STYLE, opacity: confirm.isPending || confirmMessage !== null ? 0.5 : 1, cursor: confirm.isPending || confirmMessage !== null ? "not-allowed" : "pointer" }}>{confirm.isPending ? "Confirming…" : "Confirm shelf life"}</button></div>{confirmMessage && <div role="status" className="text-success" style={{ marginTop: 8 }}>{confirmMessage}</div>}{confirmError && <div role="alert" className="text-danger" style={{ marginTop: 8 }}>{confirmError}</div>}</div>}</section> : candidate && <><CandidateCard candidate={candidate} householdId={householdId} busy={decision.isPending} onDecision={(action, fields) => decision.mutate({ action, fields })} splitItemCount={splitItemCount} onSplit={() => { if (splitItemCount != null) split.mutate(Array.from({ length: splitItemCount }, (_, index) => index)); }} splitBusy={split.isPending} />{decisionAsset && !candidate.asset_id && <div role="status" style={{ marginTop: 10 }}><Link className="text-link focus-ring" to={`/assets/${decisionAsset.assetId}?household_id=${householdId}`}>{decisionAsset.duplicate ? "Open the existing item" : "Open the item"}</Link></div>}{decision.error && <div role="alert" style={{ marginTop: 10 }}>{decision.error.message}</div>}{split.error && <div role="alert" style={{ marginTop: 10 }}>{split.error.message}</div>}{splitChildren.length > 0 && <section aria-label="Split candidates" style={{ marginTop: 16 }}><h2>Split into {splitChildren.length} items</h2><ul>{splitChildren.map((child) => <li key={child.id}><Link className="text-link focus-ring" to={`/review/${child.id}?household_id=${householdId}`}>{splitChildLabel(child)}</Link></li>)}</ul></section>}{keyboardAction && <div role="status" data-testid="keyboard-action">Keyboard: {keyboardAction}</div>}</>}</PageContainer>;
}
