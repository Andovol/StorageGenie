import type { JobStep } from "../api/types";

/**
 * SG-301 G2: one shared plain-words map for every enum the owner can see.
 * SG-307 reuses this for the catalog and the item panel.
 * Raw ids, HTTP terms and code sentences are removed at the call site,
 * never reworded through this map.
 */

export const STEP_STATE_LABELS: Record<string, string> = {
  COMPLETED: "Done",
  SUCCEEDED: "Done",
  DONE: "Done",
  AWAITING_REVIEW: "Waiting for you",
  FAILED: "Needs attention",
  ERROR: "Needs attention",
  // SG-318 W9: PENDING only waits — "Not started". "In progress" is only
  // for running states below; everything not started reads "Not started".
  PENDING: "Not started",
  QUEUED: "Not started",
  CREATED: "Not started",
  RUNNING: "In progress",
  PROCESSING: "In progress",
  IN_PROGRESS: "In progress",
  RETRYING: "In progress",
  CANCELLED: "Stopped",
};

export function labelStepState(state: string): string {
  const key = (state ?? "").toUpperCase();
  return STEP_STATE_LABELS[key] ?? "Not started";
}

export function labelJobState(state: string): string {
  return labelStepState(state);
}

export function labelSkippedStep(): string {
  return "Skipped (AI off)";
}

export function labelStepStatus(step: JobStep): string {
  const output = step.output as Record<string, unknown> | null;
  if (output && typeof output === "object" && output.status === "skipped") {
    return labelSkippedStep();
  }
  return labelStepState(step.state);
}

export const CANDIDATE_STATE_LABELS: Record<string, string> = {
  proposed: "Waiting for you",
  accepted: "Done",
  rejected: "Not kept",
  split: "Split item",
  merged: "Combined",
  held: "On hold",
};

export function labelCandidateState(state: string): string {
  return CANDIDATE_STATE_LABELS[state] ?? "Not started";
}

export const TASK_TYPE_LABELS: Record<string, string> = {
  identifier_collision: "Possible duplicate",
  "expiry.manual_entry": "Date needed",
  "candidate.multi_item": "Multiple items",
  review: "Review",
};

export function labelTaskType(taskType: string): string {
  if (TASK_TYPE_LABELS[taskType]) return TASK_TYPE_LABELS[taskType];
  return taskType.replace(/[_.]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export const TASK_PRIORITY_LABELS: Record<string, string> = {
  high: "High",
  medium: "Medium",
  low: "Low",
};

export function labelTaskPriority(priority: string): string {
  return TASK_PRIORITY_LABELS[priority] ?? priority.replace(/\b\w/g, (c) => c.toUpperCase());
}

export const TASK_STATUS_LABELS: Record<string, string> = {
  open: "Open",
  resolved: "Done",
};

export function labelTaskStatus(status: string): string {
  return TASK_STATUS_LABELS[status] ?? status.replace(/\b\w/g, (c) => c.toUpperCase());
}

export function labelSubjectKind(kind: string): string {
  if (kind === "asset") return "item";
  if (kind === "candidate") return "candidate";
  return "item";
}

export const ASSET_TYPE_LABELS: Record<string, string> = {
  product: "Product",
  unknown: "Uncategorized",
  // SG-307r1 fix 2: the expiry category words in exactly the taxonomy's own
  // spelling. The Expiry page reads these names from the served taxonomy
  // (GET /v1/taxonomy, expiry-tracker plugin categories[].name — defined in
  // backend/app/plugins/expiry_tracker.py CATEGORIES), so this map reuses
  // that one source instead of title-casing the key (which read
  // "Food Beverages" for food_beverages).
  food_beverages: "Food & beverages",
  medicine_pharma: "Medicine/pharma",
  cosmetics_personal_care: "Cosmetics/personal care",
  household_chemicals: "Household chemicals",
  documents_other: "Documents/other",
  non_perishable: "Non-perishable",
};

export function labelAssetType(assetType: string): string {
  if (ASSET_TYPE_LABELS[assetType]) return ASSET_TYPE_LABELS[assetType];
  return assetType.replace(/[_.]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export const UNNAMED_ITEM = "Unnamed item";

/**
 * SG-307 G1: the catalog's pipeline states in owner words. The card shows
 * what exists for the owner, not the pipeline stage name: only the photo,
 * a cut-out, or a scene. Failed matches the shared "Needs attention"
 * wording used for job steps.
 */
export const PRODUCT_STATUS_LABELS: Record<string, string> = {
  raw: "Photo only",
  processed: "Cut-out ready",
  rendered: "Scene ready",
  failed: "Needs attention",
};

export function labelProductStatus(status: string): string {
  return PRODUCT_STATUS_LABELS[status] ?? status.replace(/[_.]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * SG-312 G1.3 / G1.5: the plain words an owner sees for a job step, a job
 * date and an expiry state. Raw backend names never reach the screen.
 */
const STEP_NAME_LABELS: Record<string, string> = {
  EXTRACTING_DETERMINISTIC_SIGNALS: "Checking the file",
  NORMALIZING: "Tidying the details",
  DEDUPLICATING: "Looking for duplicates",
  COMMITTING: "Saving",
  AWAITING_REVIEW: "Your review",
  // SG-318 W10: the three backend steps SG-313 I5 caught without a map.
  // "Checking your upload" (it validates what you just sent, not a file in
  // general); "Reading the photo" (the AI step reads the picture — the owner
  // never needs the word AI or the -ing-with-underscore name); "Making items"
  // (candidates become items in your catalog — "items" is the owner word,
  // not "candidates").
  VALIDATING_INPUT: "Checking your upload",
  ANALYZING_WITH_AI: "Reading the photo",
  BUILDING_CANDIDATES: "Making items",
};

function sentenceCase(text: string): string {
  const lower = text.trim().toLowerCase();
  return lower.charAt(0).toUpperCase() + lower.slice(1);
}

export function labelStepName(stepName: string): string {
  const raw = stepName ?? "";
  const key = raw.toUpperCase();
  if (STEP_NAME_LABELS[key]) return STEP_NAME_LABELS[key];
  return sentenceCase(raw.replace(/[_.]+/g, " "));
}

const MONTH_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MONTH_LONG = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/**
 * SG-318 W2/W7: one shared date-only formatter — "7 Nov 2026", "" when
 * unreadable. Used by the asset Details table and the Expiry rows so both
 * read the same plain date (W3 keeps formatJobDate's Today/time form).
 */
export function formatPlainDate(value: string | null | undefined): string {
  if (!value) return "";
  const when = new Date(value);
  if (Number.isNaN(when.getTime())) return "";
  return `${when.getDate()} ${MONTH_LONG[when.getMonth()]} ${when.getFullYear()}`;
}

/** "12 Nov, 14:42", or "Today, 14:42" for the current local day; "" when unreadable. */
export function formatJobDate(value: string | null | undefined, now: Date = new Date()): string {
  if (!value) return "";
  const when = new Date(value);
  if (Number.isNaN(when.getTime())) return "";
  const time = `${String(when.getHours()).padStart(2, "0")}:${String(when.getMinutes()).padStart(2, "0")}`;
  const sameDay =
    when.getFullYear() === now.getFullYear() &&
    when.getMonth() === now.getMonth() &&
    when.getDate() === now.getDate();
  if (sameDay) return `Today, ${time}`;
  return `${when.getDate()} ${MONTH_SHORT[when.getMonth()]}, ${time}`;
}

const EXPIRY_STATE_LABELS: Record<string, string> = {
  accepted: "Date confirmed",
  proposed: "Date to confirm",
  needs_evidence: "Needs a date",
  superseded: "Replaced",
  rejected: "Not kept",
  "No date": "No date",
};

export function labelExpiryState(state: string): string {
  if (EXPIRY_STATE_LABELS[state]) return EXPIRY_STATE_LABELS[state];
  return sentenceCase((state ?? "").replace(/[_.]+/g, " "));
}
