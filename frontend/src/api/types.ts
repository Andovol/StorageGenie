export type Household = { id: string; name: string; created_at: string };
export type User = { id: string; household_id: string; display_name: string; email: string | null };
export type Evidence = {
  id: string;
  sha256: string;
  storage_key: string;
  media_type: string;
  original_filename: string;
  size_bytes: number;
};
export type Assertion = {
  id: string;
  field_path: string;
  value: unknown;
  source_type: string;
  review_state: string;
  confidence: number | null;
  source_evidence_ids: string[] | null;
  created_at: string | null;
};
export type AuditEvent = {
  id: string;
  actor: string;
  action: string;
  before: unknown;
  after: unknown;
  timestamp: string | null;
};
export type Asset = {
  id: string;
  household_id: string;
  display_name: string | null;
  asset_type: string;
  status: string;
  quantity: number | null;
  unit: string | null;
  condition: string | null;
  version: number;
  created_at: string;
  updated_at: string | null;
  evidence?: Evidence[];
  // SG-064 G3: the list serializer sends the evidence ids (not the full
  // evidence records), which is all the catalog card thumbnail reads.
  evidence_ids?: string[];
  assertions?: Assertion[];
  audit_events?: AuditEvent[];
  // SG-113: present only when the backend dormancy flag is ON; absent (not
  // empty) when the location tree is dormant, so the section hides cleanly.
  locations?: Location[];
};
export type AssetListResponse = {
  items: Asset[];
  next_cursor: string | null;
};

// SG-113: a node of one household's location tree.
export type Location = {
  id: string;
  household_id: string;
  name: string;
  parent_id: string | null;
  created_at: string | null;
  updated_at: string | null;
};
export type LocationListResponse = { items: Location[] };

// SG-068: a saved search stores EXACTLY the catalog filter surface the list
// endpoint already takes — no separate query language.
export type SavedSearchQuery = {
  q?: string;
  asset_type?: string;
  status?: string;
  has_evidence?: boolean;
};

export type SavedSearch = {
  id: string;
  household_id: string;
  name: string;
  query: SavedSearchQuery;
  created_at: string | null;
};

export type SavedSearchListResponse = { items: SavedSearch[] };

export type JobStep = {
  id: string;
  step_name: string;
  state: string;
  attempts: number;
  input: unknown;
  output: Record<string, unknown> | null;
  error: string | null;
};

export type JobProgress = { completed: number; total: number; failed: number; pending: number };
export type Job = {
  id: string;
  job_type: string;
  state: string;
  household_id: string;
  created_at: string | null;
  updated_at: string | null;
  steps?: JobStep[];
  progress?: JobProgress;
  errors?: string[];
};
export type JobListResponse = { items: Job[]; next_cursor: string | null; total: number };

export type ReviewTask = {
  id: string;
  task_type: string;
  priority: string;
  subject_ref: string;
  proposed_change: unknown;
  status: string;
  household_id: string;
  created_at: string | null;
  updated_at: string | null;
};
export type ReviewTaskListResponse = { items: ReviewTask[]; next_cursor: string | null; total: number };

export type CandidateField = unknown | { value?: unknown; confidence?: number | null; source_type?: string; source?: string };
export type DedupMatch = { type: string; asset_id?: string; evidence_id?: string; identifier?: string; distance?: number };
export type Candidate = {
  id: string;
  state: string;
  job_id: string;
  fields: Record<string, CandidateField>;
  dedup_matches: DedupMatch[];
  review_task_ids: string[];
  evidence_ids: string[];
  asset_id?: string | null;
};

export type CandidateSplitChild = {
  id: string;
  state: string;
  job_id: string;
  fields: Record<string, CandidateField>;
  evidence_ids: string[];
  split_item_index?: number | null;
};
export type CandidateSplitResponse = {
  candidate_id: string;
  state: string;
  resolved_task_ids: string[];
  children: CandidateSplitChild[];
};

export type AiSettings = {
  provider_id: string;
  model_id: string;
  allowed_model_ids: string[];
  consent: boolean;
  per_job_cap: number | null;
  monthly_cap: number | null;
  prompt_category: string;
};

export type PlanningBackingRef = {
  type: string;
  id?: string;
  label?: string | null;
  category?: string | null;
  field_path?: string;
  value?: unknown;
};

export type PlanningSuggestionBody = {
  rationale?: string[];
  expiry_date?: string | null;
  opened_date?: string | null;
  confidence?: number;
  asset_ref?: string | null;
};

export type PlanningSuggestion = {
  id: string;
  household_id: string;
  kind: string;
  title: string;
  body: PlanningSuggestionBody | null;
  backing_refs: PlanningBackingRef[];
  status: string;
  created_at: string | null;
  updated_at: string | null;
};

export type PlanningSuggestionListResponse = {
  items: PlanningSuggestion[];
  total: number;
};

export type PlanningRunResult = {
  status: string;
  reason?: string;
  suggestion_count: number;
  catalog_size: number;
  provider?: string | null;
  model?: string | null;
  guardrail_event_id?: string;
  provider_call_ids?: string[];
};

export type ChatMessage = {
  role: "user" | "assistant";
  text: string;
};

export type ChatResponse = {
  status: string;
  reason?: string | null;
  answer?: string | null;
  grounded: boolean;
  empty_catalogue: boolean;
  category: string;
  catalogue_size: number;
  provider?: string | null;
  model?: string | null;
  provider_call_id?: string | null;
  usage?: Record<string, unknown>;
  cost?: number;
  latency_ms?: number;
};

export type ChatCorrectionResponse = {
  id: string;
  kind: string;
  category: string;
  message: string;
  created_at: string | null;
};

// SG-066: deterministic household stats (GET /v1/analytics/summary). Every
// stat carries the table+query string it was read through.
export type AnalyticsStat = {
  id: string;
  label: string;
  value: unknown;
  source: string;
};

export type AnalyticsCategoryInfo = { id: string; name: string };

export type AnalyticsSummary = {
  household_id: string;
  as_of_date: string;
  generated_at: string;
  assets: { total: number; active: number; by_status: Record<string, number> };
  categories: {
    taxonomy: AnalyticsCategoryInfo[];
    counts: Record<string, number>;
    uncategorized: number;
  };
  expiry: Record<string, number>;
  waste: { expired_untouched: number };
  adherence: {
    suggestions: Record<string, number>;
    review_tasks: Record<string, number>;
  };
  stats: AnalyticsStat[];
};

export type AnalyticsInsightResult = {
  status: string;
  reason?: string | null;
  summary?: string | null;
  sentences: string[];
  cited_stat_ids: string[];
  cited_stats?: AnalyticsStat[];
  unresolved_stat_ids?: string[];
  provider?: string | null;
  model?: string | null;
  provider_call_ids?: string[];
  guardrail_event_id?: string;
  usage?: Record<string, unknown>;
  cost?: number;
  latency_ms?: number;
};

// SG-065: the served plugin taxonomy (GET /v1/taxonomy). Descriptors are
// immutable server-side, so the frontend never re-derives the list.
export type TaxonomyCategory = {
  id: string;
  name: string;
  active: boolean;
  notification: string;
  opened_date_tracking: boolean;
  chat: string;
};

export type TaxonomyPlugin = {
  plugin_id: string;
  version: string;
  categories: TaxonomyCategory[];
  date_types: string[];
  units: string[];
};

export type TaxonomyResponse = {
  plugins: TaxonomyPlugin[];
};

// SG-108: the expiry dashboard reads the SG-107 engine route
// (GET /v1/plugins/expiry-tracker/status). Keys mirror that response exactly.
export type ExpiryBucket = "expired" | "this-week" | "this-month" | "safe";
export type ExpiryTier = "critical" | "urgent" | "upcoming" | "long_lead" | "safe";
export type ExpiryUnresolvedReason =
  | "proposed"
  | "needs_evidence"
  | "unparseable"
  | "dateless";

export type ExpiryStatusRow = {
  asset_id: string;
  display_name: string | null;
  category: string;
  expiry_date: string;
  date_type: string | null;
  days_remaining: number;
  tier: ExpiryTier | null;
  bucket: ExpiryBucket;
};

export type ExpiryUnresolvedRow = {
  asset_id: string;
  reason: ExpiryUnresolvedReason;
};

export type ExpiryStatusResponse = {
  household_id: string;
  as_of: string;
  category: string | null;
  rows: ExpiryStatusRow[];
  summary: {
    by_tier: Record<string, number>;
    by_bucket: Record<string, number>;
    unresolved: number;
    total: number;
  };
  unresolved_rows: ExpiryUnresolvedRow[];
};
