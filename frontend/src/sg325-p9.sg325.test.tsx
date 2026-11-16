import { describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { CandidateCard, type DuplicateOf } from "./components/CandidateCard";
import type { Candidate } from "./api/types";

// SG-325 P9: a duplicate photo must not offer Save edits (it posts `edit` and
// the commit then takes the duplicate path, losing an edited date). The edited
// values still travel with It's another pack. Shapes copy
// CandidateCard.sg304.test.tsx (the API's candidate shape).
const duplicate: Candidate = {
  id: "candidate-325-p9",
  state: "proposed",
  job_id: "job-325-p9",
  evidence_ids: ["evidence-325-p9"],
  fields: { display_name: { value: "Olive Oil", confidence: 0.97, source_type: "ocr" }, identifier: null },
  dedup_matches: [{ type: "duplicate_of_asset", asset_id: "asset-olive-325-p9", evidence_id: "evidence-325-p9" }],
  review_task_ids: [],
  blocking_review_task_ids: [],
};

const existing: DuplicateOf = { name: "Olive Oil", expiry: "2030-05-06" };

function renderCard(candidate: Candidate, duplicateOf: DuplicateOf | null, onDecision = vi.fn()) {
  render(
    <MemoryRouter>
      <CandidateCard candidate={candidate} householdId="hh-325-p9" onDecision={onDecision} duplicateOf={duplicateOf} />
    </MemoryRouter>
  );
  return onDecision;
}

describe("SG-325 P9 duplicate hides Save edits", () => {
  test("a duplicate card shows no Save edits, and an edited name travels with It's another pack", () => {
    const onDecision = renderCard(duplicate, existing);

    expect(screen.queryByRole("button", { name: "Save edits" })).not.toBeInTheDocument();

    fireEvent.change(screen.getByDisplayValue("Olive Oil"), { target: { value: "Olive Oil Edited" } });
    fireEvent.click(screen.getByRole("button", { name: "It's another pack" }));
    expect(onDecision).toHaveBeenLastCalledWith(
      "accept",
      expect.objectContaining({ display_name: "Olive Oil Edited" }),
      { asNewPack: true }
    );
  });

  test("a non-duplicate card keeps Save edits", () => {
    renderCard({ ...duplicate, dedup_matches: [] }, null);

    expect(screen.getByRole("button", { name: "Save edits" })).toBeInTheDocument();
  });
});
