import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { apiGet, candidateDecision } from "../api/client";
import type { Candidate } from "../api/types";
import { CandidateCard } from "../components/CandidateCard";
import { ExpiryEntryForm } from "../components/ExpiryEntryForm";

export function ReviewPage() {
  const { candidateId = "" } = useParams();
  const [search] = useSearchParams();
  const householdId = search.get("household_id") || localStorage.getItem("household_id") || "";
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [assetId, setAssetId] = useState<string | null>(null);
  const [keyboardAction, setKeyboardAction] = useState("");
  const candidateQuery = useQuery<Candidate>({ queryKey: ["candidate", candidateId, householdId], queryFn: () => apiGet<Candidate>(`/v1/candidates/${candidateId}`, { household_id: householdId }), enabled: !!candidateId && !!householdId });
  useEffect(() => { if (candidateQuery.data?.asset_id) setAssetId(candidateQuery.data.asset_id); }, [candidateQuery.data?.asset_id]);
  const decision = useMutation({ mutationFn: ({ action, fields }: { action: "accept" | "edit" | "hold" | "reject"; fields?: Record<string, unknown> }) => candidateDecision(candidateId, householdId, action, fields), onSuccess: (result) => { if (result.asset_id) setAssetId(result.asset_id); qc.invalidateQueries({ queryKey: ["candidate", candidateId, householdId] }); } });
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

  return <div style={{ padding: 24, maxWidth: 1100 }}><Link to={`/inbox?household_id=${householdId}`}>← Back to inbox</Link><h1>Review workspace</h1>{candidateQuery.isLoading && <div>Loading candidate…</div>}{candidateQuery.error && <div role="alert">{candidateQuery.error.message}</div>}{candidate && <><CandidateCard candidate={candidate} householdId={householdId} busy={decision.isPending} onDecision={(action, fields) => decision.mutate({ action, fields })} />{decision.error && <div role="alert" style={{ marginTop: 10 }}>{decision.error.message}</div>}{keyboardAction && <div role="status" data-testid="keyboard-action">Keyboard: {keyboardAction}</div>}{assetId && <ExpiryEntryForm assetId={assetId} householdId={householdId} evidenceIds={candidate.evidence_ids} />}</>}</div>;
}
