import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { CandidateCard } from "./CandidateCard";

const candidate = {
  id: "candidate-271",
  state: "proposed",
  job_id: "job-271",
  fields: {
    display_name: { value: "Milk", confidence: 0.9, source_type: "extraction" },
    asset_type: { value: "product", confidence: null, source_type: "deterministic" },
    category_proposed: { value: "food_beverages", confidence: 0.9, source_type: "extraction" },
  },
  dedup_matches: [],
  review_task_ids: [],
  blocking_review_task_ids: [],
  evidence_ids: [],
};

describe("CandidateCard SG-271 G4", () => {
  test("kind and shelf life never both read as category", () => {
    render(
      <QueryClientProvider client={new QueryClient()}>
        <MemoryRouter>
          <CandidateCard candidate={candidate} householdId="hh-271" onDecision={() => {}} />
        </MemoryRouter>
      </QueryClientProvider>
    );
    expect(screen.getByText("Kind of item")).toBeInTheDocument();
    expect(screen.getByText("Suggested shelf life")).toBeInTheDocument();
    expect(screen.queryByText("asset_type")).not.toBeInTheDocument();
    expect(screen.queryByText("category_proposed")).not.toBeInTheDocument();
  });
});
