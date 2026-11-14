import { describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { JobCard } from "./components/JobCard";
import { formatJobDate, labelStepStatus } from "./lib/labels";

function skippedStep(id: string) {
  return { id, step_name: "ANALYZING_WITH_AI", state: "COMPLETED", attempts: 1, input: null, output: { status: "skipped", reason: "consent_disabled" }, error: null };
}

function doneStep(id: string, name: string) {
  return { id, step_name: name, state: "COMPLETED", attempts: 1, input: null, output: { status: "ok", step: name }, error: null };
}

describe("SG-324 P6 inbox", () => {
  test("progress excludes skipped steps from done and total", () => {
    const job = {
      id: "job-p6",
      job_type: "import",
      state: "COMPLETED",
      household_id: "hh",
      created_at: "2026-10-01T19:30:00+00:00",
      updated_at: null,
      steps: [
        doneStep("s1", "VALIDATING_INPUT"),
        doneStep("s2", "NORMALIZING"),
        doneStep("s3", "EXTRACTING_DETERMINISTIC_SIGNALS"),
        doneStep("s4", "DEDUPLICATING"),
        skippedStep("s5"),
        skippedStep("s6"),
      ],
      progress: { completed: 6, total: 6, failed: 0, pending: 0 },
    };
    render(<JobCard job={job} selected={false} onSelect={vi.fn()} />);
    expect(screen.getByText("4 of 4 steps done · 2 skipped")).toBeInTheDocument();
  });

  test("a job is named by when it was made", () => {
    const created = "2026-10-01T19:30:00+00:00";
    const job = {
      id: "job-p6-name",
      job_type: "import",
      state: "COMPLETED",
      household_id: "hh",
      created_at: created,
      updated_at: null,
      progress: { completed: 1, total: 1, failed: 0, pending: 0 },
    };
    render(<JobCard job={job} selected={false} onSelect={vi.fn()} />);
    const expected = `Import · ${formatJobDate(created)}`;
    expect(screen.getByText(expected)).toBeInTheDocument();
  });

  test("a skipped step reads photo reading is off", () => {
    expect(
      labelStepStatus({ id: "s", step_name: "ANALYZING_WITH_AI", state: "COMPLETED", attempts: 1, input: null, output: { status: "skipped", reason: "consent_disabled" }, error: null })
    ).toBe("Skipped — photo reading is off");
  });
});
