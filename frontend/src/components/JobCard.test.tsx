import { describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { JobCard } from "./JobCard";

describe("JobCard", () => {
  test("renders loaded job id, state, and progress", () => {
    render(<JobCard job={{ id: "job-loaded-42", job_type: "import", state: "FAILED", household_id: "household-1", created_at: null, updated_at: null, progress: { completed: 2, total: 6, failed: 1, pending: 3 } }} selected={false} onSelect={vi.fn()} />);
    expect(screen.getByText("Import job")).toBeInTheDocument();
    expect(screen.getByText("Needs attention")).toBeInTheDocument();
    expect(screen.getByText(/2\/6 complete/)).toBeInTheDocument();
  });

  test("title and status carry theme text classes with the state tone (SG-105 G3)", () => {
    const base = { id: "job-loaded-42", job_type: "import", household_id: "household-1", created_at: null, updated_at: null };
    const { rerender } = render(<JobCard job={{ ...base, state: "FAILED" }} selected={false} onSelect={vi.fn()} />);

    // The whole card is a button: without a theme text colour it renders the
    // browser-default black on the dark card.
    expect(screen.getByRole("button")).toHaveClass("focus-ring");
    expect(screen.getByText("Needs attention")).toHaveClass("text-danger");

    rerender(<JobCard job={{ ...base, state: "COMPLETED" }} selected={false} onSelect={vi.fn()} />);
    expect(screen.getByText("Done")).toHaveClass("text-success");

    rerender(<JobCard job={{ ...base, state: "PROCESSING" }} selected={false} onSelect={vi.fn()} />);
    expect(screen.getByText("In progress")).toHaveClass("text-processed");

    rerender(<JobCard job={{ ...base, state: "QUEUED" }} selected={false} onSelect={vi.fn()} />);
    expect(screen.getByText("In progress")).toHaveClass("text-muted-foreground");
  });
});
