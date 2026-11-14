import { describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { CandidateCard } from "./components/CandidateCard";
import type { Candidate } from "./api/types";

const candidate: Candidate = {
  id: "candidate-loaded-7",
  state: "proposed",
  job_id: "job-loaded-7",
  evidence_ids: ["photo-g2", "transcript-g2"],
  fields: { display_name: { value: "Camera", confidence: 0.94, source_type: "ocr" } },
  dedup_matches: [],
  review_task_ids: [],
  blocking_review_task_ids: [],
};

describe("SG-324 T1 review card fallback", () => {
  test("a failed thumb reads No photo yet, never Thumbnail unavailable", () => {
    render(
      <MemoryRouter>
        <CandidateCard candidate={candidate} householdId="h" onDecision={vi.fn()} />
      </MemoryRouter>
    );
    const article = screen.getByRole("article");
    const images = article.querySelectorAll("img");
    expect(images).toHaveLength(2);
    fireEvent.error(images[1]);
    expect(screen.getByText("No photo yet")).toBeInTheDocument();
    expect(screen.queryByText("Thumbnail unavailable")).toBeNull();
  });
});
