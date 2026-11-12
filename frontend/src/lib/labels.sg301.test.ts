import { describe, expect, test } from "vitest";
import {
  UNNAMED_ITEM,
  labelCandidateState,
  labelJobState,
  labelStepStatus,
  labelSubjectKind,
  labelTaskPriority,
  labelTaskStatus,
  labelTaskType,
} from "./labels";

describe("SG-301 labels", () => {
  test("step COMPLETED reads Done", () => {
    expect(labelJobState("COMPLETED")).toBe("Done");
  });
  test("step AWAITING_REVIEW reads Waiting for you", () => {
    expect(labelJobState("AWAITING_REVIEW")).toBe("Waiting for you");
  });
  test("skipped output reads Skipped (AI off)", () => {
    expect(
      labelStepStatus({ id: "s", step_name: "X", state: "COMPLETED", attempts: 1, input: null, output: { status: "skipped", reason: "consent_disabled" }, error: null })
    ).toBe("Skipped (AI off)");
  });
  test("skipped output never reads Done", () => {
    const label = labelStepStatus({ id: "s", step_name: "X", state: "COMPLETED", attempts: 1, input: null, output: { status: "skipped" }, error: null });
    expect(label).not.toBe("Done");
  });
  test("candidate split reads Split item", () => {
    expect(labelCandidateState("split")).toBe("Split item");
  });
  test("task identifier_collision reads Possible duplicate", () => {
    expect(labelTaskType("identifier_collision")).toBe("Possible duplicate");
  });
  test("task priority high reads High", () => {
    expect(labelTaskPriority("high")).toBe("High");
  });
  test("task status open reads Open", () => {
    expect(labelTaskStatus("open")).toBe("Open");
  });
  test("unknown subject kind reads item", () => {
    expect(labelSubjectKind("unknown")).toBe("item");
  });
  test("unnamed fallback is Unnamed item", () => {
    expect(UNNAMED_ITEM).toBe("Unnamed item");
  });
});
