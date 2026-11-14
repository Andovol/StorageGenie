import { describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { CandidateCard, type DuplicateOf } from "./CandidateCard";
import type { Candidate } from "../api/types";

// SG-304 G2 (F10): a duplicate photo shows the existing item by name and date,
// never by id, with three choices.
const ASSET_ID = "asset-olive-304";

const duplicate: Candidate = {
  id: "candidate-304",
  state: "proposed",
  job_id: "job-304",
  evidence_ids: ["evidence-304"],
  fields: { display_name: { value: "Olive Oil", confidence: 0.97, source_type: "ocr" }, identifier: null },
  dedup_matches: [{ type: "duplicate_of_asset", asset_id: ASSET_ID, evidence_id: "evidence-304" }],
  review_task_ids: [],
  blocking_review_task_ids: [],
};

const existing: DuplicateOf = { name: "Olive Oil", expiry: "2030-05-06" };

function renderCard(candidate: Candidate, duplicateOf: DuplicateOf | null, onDecision = vi.fn()) {
  render(
    <MemoryRouter>
      <CandidateCard candidate={candidate} householdId="hh-304" onDecision={onDecision} duplicateOf={duplicateOf} />
    </MemoryRouter>
  );
  return onDecision;
}

describe("CandidateCard SG-304 G2 (duplicate photo)", () => {
  test("names the existing item by name and date, never by its id, and offers the three choices", () => {
    renderCard(duplicate, existing);

    expect(screen.getByText("This photo matches Olive Oil (use by 6 May 2030).")).toBeInTheDocument();
    expect(screen.getByRole("article").textContent).not.toContain(ASSET_ID);
    expect(screen.getByRole("button", { name: "It's another pack" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "It's the same pack" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Decide later" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Accept" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Hold / Unknown" })).not.toBeInTheDocument();
  });

  test("with no loaded item the line still shows no id", () => {
    renderCard(duplicate, null);

    expect(screen.getByText("This photo matches an item you already have.")).toBeInTheDocument();
    expect(screen.getByRole("article").textContent).not.toContain(ASSET_ID);
  });

  test("each choice sends its own decision: another pack with the new-pack option, the same pack plainly, decide later as hold", () => {
    const onDecision = renderCard(duplicate, existing);

    fireEvent.click(screen.getByRole("button", { name: "It's another pack" }));
    expect(onDecision).toHaveBeenLastCalledWith("accept", expect.any(Object), { asNewPack: true });

    fireEvent.click(screen.getByRole("button", { name: "It's the same pack" }));
    expect(onDecision).toHaveBeenLastCalledWith("accept", expect.any(Object));
    expect(onDecision.mock.calls[1]).toHaveLength(2);

    fireEvent.click(screen.getByRole("button", { name: "Decide later" }));
    expect(onDecision).toHaveBeenLastCalledWith("hold");
    expect(onDecision).toHaveBeenCalledTimes(3);
  });

  test("a candidate with no duplicate keeps Accept and Hold / Unknown", () => {
    const onDecision = renderCard({ ...duplicate, dedup_matches: [] }, null);

    expect(screen.queryByRole("button", { name: "It's another pack" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Accept" }));
    expect(onDecision).toHaveBeenLastCalledWith("accept", expect.any(Object));
    fireEvent.click(screen.getByRole("button", { name: "Hold / Unknown" }));
    expect(onDecision).toHaveBeenLastCalledWith("hold");
  });
});
