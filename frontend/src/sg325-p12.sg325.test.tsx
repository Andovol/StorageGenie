import { describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { CandidateCard, type DuplicateOf } from "./components/CandidateCard";
import type { Candidate } from "./api/types";

// SG-325 P12: the review card speaks plain words. The candidate shape copies
// CandidateCard.sg304.test.tsx, plus the use-by and status fields the API
// sends (raw keys display_name/expiry_date/status/identifier).
const candidate: Candidate = {
  id: "candidate-325-p12",
  state: "proposed",
  job_id: "job-325-p12",
  evidence_ids: ["evidence-325-p12"],
  fields: {
    display_name: { value: "Olive Oil", confidence: 0.97, source_type: "ocr" },
    expiry_date: { value: "2032-06-18", confidence: 0.9, source_type: "ocr" },
    identifier: null,
    status: { value: "ACTIVE", confidence: null, source_type: "deterministic" },
  },
  dedup_matches: [{ type: "identifier_collision", identifier: "SN-1", asset_id: "asset-1" }],
  review_task_ids: [],
  blocking_review_task_ids: [],
};

const duplicate: Candidate = {
  ...candidate,
  id: "candidate-325-p12-dup",
  dedup_matches: [{ type: "duplicate_of_asset", asset_id: "asset-olive-325", evidence_id: "evidence-325-p12" }],
};

const existing: DuplicateOf = { name: "Olive Oil", expiry: "2030-05-06" };

function renderCard(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe("SG-325 P12 review card plain words", () => {
  test("heading reads Check this item with no id, state, job, or review tag", () => {
    renderCard(<CandidateCard candidate={candidate} householdId="h" onDecision={vi.fn()} />);

    expect(screen.getByRole("heading", { name: "Check this item" })).toBeInTheDocument();
    expect(screen.queryByText(/Candidate candidate-325-p12/)).not.toBeInTheDocument();
    expect(screen.queryByText(/State:/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Job:/)).not.toBeInTheDocument();
    expect(screen.queryByText("Candidate review")).not.toBeInTheDocument();
  });

  test("the collision warning reads plain words with no advisory sentence", () => {
    renderCard(<CandidateCard candidate={candidate} householdId="h" onDecision={vi.fn()} />);

    expect(screen.getByText("This may already be in your catalog")).toBeInTheDocument();
    expect(screen.queryByText("Possible duplicates or collisions")).not.toBeInTheDocument();
    expect(screen.queryByText("This match is advisory; review it before accepting.")).not.toBeInTheDocument();
  });

  test("sections read What we read and Photo", () => {
    renderCard(<CandidateCard candidate={candidate} householdId="h" onDecision={vi.fn()} />);

    expect(screen.getByRole("region", { name: "What we read" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "What we read" })).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Photo" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Photo" })).toBeInTheDocument();
    expect(screen.queryByRole("region", { name: "Candidate fields" })).not.toBeInTheDocument();
    expect(screen.queryByRole("region", { name: "Source evidence" })).not.toBeInTheDocument();
  });

  test("every field key has a plain label and no raw key shows", () => {
    renderCard(<CandidateCard candidate={candidate} householdId="h" onDecision={vi.fn()} />);

    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Use by")).toBeInTheDocument();
    expect(screen.getByText("Status")).toBeInTheDocument();
    expect(screen.getByText("Identifier")).toBeInTheDocument();
    expect(screen.queryByText("display_name")).not.toBeInTheDocument();
    expect(screen.queryByText("expiry_date")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Name")).toBeInTheDocument();
    expect(screen.getByLabelText("Use by")).toBeInTheDocument();
  });

  test("the use-by field is a date field and its edited value posts as YYYY-MM-DD", () => {
    const onDecision = vi.fn();
    renderCard(<CandidateCard candidate={candidate} householdId="h" onDecision={onDecision} />);

    const useBy = screen.getByLabelText("Use by");
    expect(useBy).toHaveAttribute("type", "date");
    expect(useBy).toHaveValue("2032-06-18");
    fireEvent.change(useBy, { target: { value: "2031-01-05" } });
    fireEvent.click(screen.getByRole("button", { name: "Accept" }));
    expect(onDecision).toHaveBeenLastCalledWith("accept", expect.objectContaining({ expiry_date: "2031-01-05" }));
  });

  test("the confidence line reads at 13px and no evidence id shows under the photo", () => {
    renderCard(<CandidateCard candidate={candidate} householdId="h" onDecision={vi.fn()} />);

    const lines = screen.getAllByText(/Confidence:/);
    expect(lines.length).toBeGreaterThan(0);
    for (const line of lines) expect(line.style.fontSize).toBe("13px");
    expect(screen.queryByText("evidence-325-p12")).not.toBeInTheDocument();
  });

  test("the duplicate choices keep the themed control size", () => {
    renderCard(
      <CandidateCard candidate={duplicate} householdId="h" onDecision={vi.fn()} duplicateOf={existing} />
    );

    for (const name of ["It's another pack", "It's the same pack", "Decide later"]) {
      const button = screen.getByRole("button", { name });
      expect(Number.parseFloat(button.style.fontSize)).toBeGreaterThanOrEqual(13);
    }
  });
});
