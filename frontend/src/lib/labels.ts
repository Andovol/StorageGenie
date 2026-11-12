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
  PENDING: "In progress",
  RUNNING: "In progress",
  PROCESSING: "In progress",
  IN_PROGRESS: "In progress",
  RETRYING: "In progress",
  CREATED: "In progress",
  CANCELLED: "Stopped",
};

export function labelStepState(state: string): string {
  const key = (state ?? "").toUpperCase();
  return STEP_STATE_LABELS[key] ?? "In progress";
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
  return CANDIDATE_STATE_LABELS[state] ?? "In progress";
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
};

export function labelAssetType(assetType: string): string {
  if (ASSET_TYPE_LABELS[assetType]) return ASSET_TYPE_LABELS[assetType];
  return assetType.replace(/[_.]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export const UNNAMED_ITEM = "Unnamed item";
