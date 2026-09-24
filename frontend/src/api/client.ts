import type {
  AiSettings,
  AnalyticsInsightResult,
  AnalyticsSummary,
  Assertion,
  CandidateSplitResponse,
  ChatCorrectionResponse,
  ChatResponse,
  ExpiryStatusResponse,
  LocationListResponse,
  PlanningRunResult,
  PlanningSuggestion,
  PlanningSuggestionListResponse,
} from "./types";

const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8003";

export function buildUrl(path: string, params: Record<string, string> = {}): string {
  const u = new URL(BASE + path);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") u.searchParams.set(k, v);
  });
  return u.toString();
}

function parseRfc9457(body: unknown, fallback: string): string {
  if (body && typeof body === "object") {
    const b = body as Record<string, unknown>;
    if (typeof b.detail === "string" && b.detail) return b.detail;
    if (typeof b.title === "string" && b.title) {
      const detail = typeof b.detail === "string" ? `: ${b.detail}` : "";
      return `${b.title}${detail}`;
    }
  }
  return fallback;
}

export async function apiGet<T>(path: string, params: Record<string, string> = {}): Promise<T> {
  const r = await fetch(buildUrl(path, params));
  if (!r.ok) {
    const body = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(parseRfc9457(body, `GET ${path} failed: ${r.status}`));
  }
  return r.json() as Promise<T>;
}

export async function apiPost<T>(
  path: string,
  body: unknown,
  params: Record<string, string> = {},
  headers: Record<string, string> = {}
): Promise<T> {
  const r = await fetch(buildUrl(path, params), {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const b = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(parseRfc9457(b, `POST ${path} failed: ${r.status}`));
  }
  return r.json() as Promise<T>;
}

export async function apiPatch<T>(
  path: string,
  body: unknown,
  params: Record<string, string> = {},
  headers: Record<string, string> = {}
): Promise<T> {
  const r = await fetch(buildUrl(path, params), {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const b = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(parseRfc9457(b, `PATCH ${path} failed: ${r.status}`));
  }
  return r.json() as Promise<T>;
}

export async function apiPut<T>(
  path: string,
  body: unknown,
  params: Record<string, string> = {},
  headers: Record<string, string> = {}
): Promise<T> {
  const r = await fetch(buildUrl(path, params), {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const b = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(parseRfc9457(b, `PUT ${path} failed: ${r.status}`));
  }
  return r.json() as Promise<T>;
}

export async function apiDelete<T>(path: string, params: Record<string, string> = {}): Promise<T> {
  const r = await fetch(buildUrl(path, params), { method: "DELETE" });
  if (!r.ok) {
    const b = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(parseRfc9457(b, `DELETE ${path} failed: ${r.status}`));
  }
  return r.json() as Promise<T>;
}

// SG-113: location tree reads/writes. Every route answers 404 while the
// backend dormancy flag is OFF; the UI treats that as "section hidden".
export function fetchLocations(householdId: string) {
  return apiGet<LocationListResponse>("/v1/locations", { household_id: householdId });
}

export function assignAssetLocation(assetId: string, locationId: string, householdId: string) {
  return apiPost<{ status: string; asset_id: string; location_id: string }>(
    `/v1/assets/${assetId}/locations`,
    { location_id: locationId },
    { household_id: householdId }
  );
}

export function unassignAssetLocation(assetId: string, locationId: string, householdId: string) {
  return apiDelete<{ status: string; asset_id: string; location_id: string }>(
    `/v1/assets/${assetId}/locations/${locationId}`,
    { household_id: householdId }
  );
}

export function fetchAiSettings() {
  return apiGet<AiSettings>("/v1/settings/ai");
}

export function updateAiModel(modelId: string) {
  return apiPut<AiSettings>("/v1/settings/ai", { model_id: modelId });
}

export async function uploadEvidence(
  householdId: string,
  file: File
): Promise<{ id: string; sha256: string; storage_key: string; size_bytes: number }> {
  const fd = new FormData();
  fd.append("file", file);
  const r = await fetch(buildUrl("/v1/evidence", { household_id: householdId }), {
    method: "POST",
    body: fd,
  });
  if (!r.ok) {
    const b = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(parseRfc9457(b, `Upload failed: ${r.status}`));
  }
  return r.json();
}

export function candidateDecision(
  candidateId: string,
  householdId: string,
  action: "accept" | "edit" | "hold" | "reject",
  correctedFields: Record<string, unknown> = {}
) {
  return apiPost<{ candidate_id?: string; id?: string; state: string; asset_id?: string }>(
    `/v1/candidates/${candidateId}/decision`,
    { action, corrected_fields: correctedFields },
    { household_id: householdId }
  );
}

export function candidateSplit(
  candidateId: string,
  householdId: string,
  itemIndexes: number[]
) {
  return apiPost<CandidateSplitResponse>(
    `/v1/candidates/${candidateId}/split`,
    { item_indexes: itemIndexes },
    { household_id: householdId }
  );
}

export function resolveReviewTask(taskId: string, householdId: string) {
  return apiPost<{ id: string; status: string }>(
    `/v1/review-tasks/${taskId}/resolve`,
    {},
    { household_id: householdId }
  );
}

export function enterManualExpiry(
  assetId: string,
  householdId: string,
  payload: { expiry_date: string; date_type: string; source_evidence_ids?: string[] }
) {
  return apiPost<{ asset_id: string; assertion: Assertion; resolved_review_task_ids: string[] }>(
    `/v1/plugins/expiry-tracker/assets/${assetId}/expiry`,
    payload,
    { household_id: householdId }
  );
}

export function runPlanning(householdId: string) {
  return apiPost<PlanningRunResult>("/v1/planning/run", {}, { household_id: householdId });
}

export function fetchPlanningSuggestions(householdId: string, status?: string) {
  return apiGet<PlanningSuggestionListResponse>("/v1/planning/suggestions", {
    household_id: householdId,
    ...(status ? { status } : {}),
  });
}

export function confirmPlanningSuggestion(suggestionId: string, householdId: string) {
  return apiPost<PlanningSuggestion>(
    `/v1/planning/suggestions/${suggestionId}/confirm`,
    {},
    { household_id: householdId }
  );
}

export function dismissPlanningSuggestion(
  suggestionId: string,
  householdId: string,
  reason?: string
) {
  return apiPost<PlanningSuggestion>(
    `/v1/planning/suggestions/${suggestionId}/dismiss`,
    { reason: reason ?? null },
    { household_id: householdId }
  );
}

export function sendChat(category: string, householdId: string, message: string) {
  return apiPost<ChatResponse>(
    `/v1/chat/${category}`,
    { message },
    { household_id: householdId }
  );
}

export function fetchAnalyticsSummary(householdId: string) {
  return apiGet<AnalyticsSummary>("/v1/analytics/summary", {
    household_id: householdId,
  });
}

// SG-108: reader for the SG-107 urgency engine. An unset category is dropped
// by `buildUrl` (empty-string params never reach the URL), so the default
// request carries only the household scope.
export function fetchExpiryStatus(householdId: string, category?: string) {
  return apiGet<ExpiryStatusResponse>("/v1/plugins/expiry-tracker/status", {
    household_id: householdId,
    category: category ?? "",
  });
}

export function generateAnalyticsInsights(householdId: string) {
  return apiPost<AnalyticsInsightResult>(
    "/v1/analytics/insights",
    {},
    { household_id: householdId }
  );
}

export function logChatCorrection(category: string, householdId: string, message: string) {
  return apiPost<ChatCorrectionResponse>(
    `/v1/chat/${category}/corrections`,
    { message },
    { household_id: householdId }
  );
}
