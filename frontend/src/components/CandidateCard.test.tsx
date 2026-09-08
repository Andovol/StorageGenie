import { describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { CandidateCard } from "./CandidateCard";
import type { Candidate } from "../api/types";

const candidate: Candidate = {
  id: "candidate-loaded-7", state: "proposed", job_id: "job-loaded-7", evidence_ids: ["evidence-loaded-7"],
  fields: { display_name: { value: "Camera", confidence: 0.94, source_type: "ocr" }, identifier: null },
  dedup_matches: [{ type: "identifier_collision", identifier: "SN-7", asset_id: "asset-7" }], review_task_ids: ["task-loaded-7"],
};

describe("CandidateCard", () => {
  test("keeps evidence beside fields and exposes confidence, source, and blocking collision", () => {
    render(<CandidateCard candidate={candidate} householdId="household-loaded-7" onDecision={vi.fn()} />);
    const article = screen.getByRole("article");
    expect(screen.getByDisplayValue("Camera")).toBeInTheDocument();
    expect(article.querySelector("img")).toHaveAttribute("src", expect.stringContaining("evidence-loaded-7"));
    expect(article).toHaveTextContent("Confidence: 0.94");
    expect(article).toHaveTextContent("Source: ocr");
    expect(article).toHaveTextContent("Acceptance is blocked");
    expect(screen.getByRole("button", { name: "Accept" })).toBeDisabled();
  });

  test("hold is a first-class action and does not invent an Unknown value", () => {
    const onDecision = vi.fn();
    render(<CandidateCard candidate={{ ...candidate, review_task_ids: [], dedup_matches: [] }} householdId="h" onDecision={onDecision} />);
    fireEvent.click(screen.getByRole("button", { name: "Hold / Unknown" }));
    expect(onDecision).toHaveBeenCalledWith("hold");
    expect(screen.getByLabelText("identifier value")).toHaveValue("");
    expect(screen.getAllByText(/Confidence:/).some((element) => element.textContent?.includes("Unknown"))).toBe(true);
  });

  test("wrong loaded candidate is discriminated by the evidence identity assertion", () => {
    render(<CandidateCard candidate={{ ...candidate, evidence_ids: ["wrong-evidence"] }} householdId="h" onDecision={vi.fn()} />);
    expect(() => expect(screen.getByRole("article").querySelector("img")).toHaveAttribute("src", expect.stringContaining("evidence-loaded-7"))).toThrow();
  });
});
