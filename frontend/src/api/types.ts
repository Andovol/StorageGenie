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
