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
  display_name: string;
  asset_type: string;
  status: string;
  quantity: number | null;
  unit: string | null;
  condition: string | null;
  version: number;
  created_at: string;
  updated_at: string | null;
  evidence?: Evidence[];
  assertions?: Assertion[];
  audit_events?: AuditEvent[];
};
export type AssetListResponse = {
  items: Asset[];
  next_cursor: string | null;
};

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
