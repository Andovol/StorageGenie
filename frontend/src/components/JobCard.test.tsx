import { describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { JobCard } from "./JobCard";

describe("JobCard", () => {
  test("renders loaded job id, state, and progress", () => {
    render(<JobCard job={{ id: "job-loaded-42", job_type: "import", state: "FAILED", household_id: "household-1", created_at: null, updated_at: null, progress: { completed: 2, total: 6, failed: 1, pending: 3 } }} selected={false} onSelect={vi.fn()} />);
    expect(screen.getByText("Import job-load")).toBeInTheDocument();
    expect(screen.getByTestId("job-state-job-loaded-42")).toHaveTextContent("FAILED");
    expect(screen.getByText(/2\/6 complete/)).toBeInTheDocument();
  });
});
