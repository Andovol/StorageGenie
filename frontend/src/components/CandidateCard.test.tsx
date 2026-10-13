import type { ReactElement } from "react";
import { describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { CandidateCard } from "./CandidateCard";
import type { Candidate } from "../api/types";

const candidate: Candidate = {
  id: "candidate-loaded-7", state: "proposed", job_id: "job-loaded-7", evidence_ids: ["evidence-loaded-7"],
  fields: { display_name: { value: "Camera", confidence: 0.94, source_type: "ocr" }, identifier: null },
  dedup_matches: [{ type: "identifier_collision", identifier: "SN-7", asset_id: "asset-7" }], review_task_ids: ["task-loaded-7"],
};

function renderCard(ui: ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe("CandidateCard", () => {
  test("keeps evidence beside fields and exposes confidence, source, and blocking collision", () => {
    renderCard(<CandidateCard candidate={candidate} householdId="household-loaded-7" onDecision={vi.fn()} />);
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
    renderCard(<CandidateCard candidate={{ ...candidate, review_task_ids: [], dedup_matches: [] }} householdId="h" onDecision={onDecision} />);
    fireEvent.click(screen.getByRole("button", { name: "Hold / Unknown" }));
    expect(onDecision).toHaveBeenCalledWith("hold");
    expect(screen.getByLabelText("identifier value")).toHaveValue("");
    expect(screen.getAllByText(/Confidence:/).some((element) => element.textContent?.includes("Unknown"))).toBe(true);
  });

  test("wrong loaded candidate is discriminated by the evidence identity assertion", () => {
    renderCard(<CandidateCard candidate={{ ...candidate, evidence_ids: ["wrong-evidence"] }} householdId="h" onDecision={vi.fn()} />);
    expect(() => expect(screen.getByRole("article").querySelector("img")).toHaveAttribute("src", expect.stringContaining("evidence-loaded-7"))).toThrow();
  });

  test("renders a brand web alternate with its source, and never the source URL as visible text (SG-119 G2)", () => {
    const sourceUrl = "https://world.openfoodfacts.org/api/v2/search?search_terms=Jacobs";
    const withBrand: Candidate = {
      ...candidate,
      review_task_ids: [],
      dedup_matches: [],
      fields: {
        brand: { value: "Jacobs", source_type: "user" },
        display_name: { value: "Coffee", source_type: "user" },
      },
      web_alternates: [
        {
          field: "brand",
          value: "Jacobs Cronat Gold",
          source_type: "web:OpenFoodFacts",
          source_url: sourceUrl,
          retrieved_at: "2026-09-25T00:00:00+00:00",
        },
      ],
    };
    renderCard(<CandidateCard candidate={withBrand} householdId="h" onDecision={vi.fn()} />);

    const section = screen.getByRole("region", { name: "Web alternates" });
    expect(within(section).getByText("brand")).toBeInTheDocument();
    expect(within(section).getByText("Jacobs Cronat Gold")).toBeInTheDocument();
    expect(within(section).getByText("web:OpenFoodFacts")).toBeInTheDocument();
    const link = within(section).getByRole("link", { name: "source" });
    expect(link).toHaveAttribute("href", sourceUrl);
    // The full URL lives in the href/title, never as visible text (SG-118 discipline).
    expect(section.textContent ?? "").not.toContain("world.openfoodfacts.org");
  });

  test("split action appears only when a multi-item count is supplied and fires once", () => {
    const onSplit = vi.fn();
    const { rerender } = renderCard(<CandidateCard candidate={{ ...candidate, review_task_ids: [] }} householdId="h" onDecision={vi.fn()} />);
    expect(screen.queryByRole("button", { name: /split/i })).toBeNull();
    rerender(<MemoryRouter><CandidateCard candidate={{ ...candidate, review_task_ids: [] }} householdId="h" onDecision={vi.fn()} splitItemCount={2} onSplit={onSplit} /></MemoryRouter>);
    const button = screen.getByRole("button", { name: /split/i });
    expect(button).toHaveTextContent("2");
    fireEvent.click(button);
    expect(onSplit).toHaveBeenCalledTimes(1);
  });

  test("blocked candidate with zero dedup matches shows a visible reason and Inbox link without hover or alert (SG-171 G1)", () => {
    renderCard(<CandidateCard candidate={{ ...candidate, review_task_ids: ["task-g1"], dedup_matches: [] }} householdId="household-g1" onDecision={vi.fn()} />);
    const article = screen.getByRole("article");
    // The reason is visible text with no alert (no dedup matches) and no hover fired.
    expect(article).toHaveTextContent("Acceptance is blocked until the open review task(s) are resolved.");
    expect(screen.queryByRole("alert")).toBeNull();
    const link = screen.getByRole("link", { name: "View them in the Inbox." });
    expect(link).toHaveAttribute("href", "/inbox?household_id=household-g1");
    expect(link).toHaveClass("text-link");
    expect(screen.getByRole("button", { name: "Accept" })).toBeDisabled();
  });

  test("unblocked candidate renders neither the reason sentence nor the Inbox link (SG-171 G1)", () => {
    renderCard(<CandidateCard candidate={{ ...candidate, review_task_ids: [], dedup_matches: [] }} householdId="h" onDecision={vi.fn()} />);
    expect(screen.queryByText("Acceptance is blocked until the open review task(s) are resolved.")).toBeNull();
    expect(screen.queryByRole("link", { name: "View them in the Inbox." })).toBeNull();
  });

  test("one photo plus one imageless evidence renders one image and one focusable fallback (SG-171 G2)", () => {
    renderCard(<CandidateCard candidate={{ ...candidate, review_task_ids: [], dedup_matches: [], evidence_ids: ["photo-g2", "transcript-g2"] }} householdId="h" onDecision={vi.fn()} />);
    const article = screen.getByRole("article");
    const imagesBefore = article.querySelectorAll("img");
    expect(imagesBefore).toHaveLength(2);
    // The imageless (non-photo) evidence 404s its thumb; the broken img is replaced, not left as an icon.
    fireEvent.error(imagesBefore[1]);
    expect(article.querySelectorAll("img")).toHaveLength(1);
    const fallback = screen.getByText("Thumbnail unavailable");
    expect(fallback).toHaveAttribute("tabindex", "0");
    expect(fallback).toHaveClass("focus-ring");
  });

  test("blocked candidate with dedup matches renders the blocked reason exactly once (SG-175 G2)", () => {
    renderCard(<CandidateCard candidate={{ ...candidate, review_task_ids: ["task-g2"] }} householdId="household-g2" onDecision={vi.fn()} />);
    const article = screen.getByRole("article");
    expect(article.textContent?.split("Acceptance is blocked until the open review task(s) are resolved.").length).toBe(2);
    expect(article).toHaveTextContent("Identifier collision: SN-7");
    expect(screen.getAllByRole("link", { name: "View them in the Inbox." })).toHaveLength(1);
    expect(screen.getByRole("button", { name: "Accept" })).toBeDisabled();
  });

  test("unblocked candidate with dedup matches keeps the advisory and no blocked reason (SG-175 G2)", () => {
    renderCard(<CandidateCard candidate={{ ...candidate, review_task_ids: [] }} householdId="h" onDecision={vi.fn()} />);
    const article = screen.getByRole("article");
    expect(article.textContent?.split("Acceptance is blocked until the open review task(s) are resolved.").length).toBe(1);
    expect(article).toHaveTextContent("This match is advisory; review it before accepting.");
    expect(screen.queryByRole("link", { name: "View them in the Inbox." })).toBeNull();
  });

  test("all-photo evidence renders zero fallback blocks (SG-171 G2)", () => {
    renderCard(<CandidateCard candidate={{ ...candidate, review_task_ids: [], dedup_matches: [], evidence_ids: ["photo-a", "photo-b"] }} householdId="h" onDecision={vi.fn()} />);
    const article = screen.getByRole("article");
    expect(article.querySelectorAll("img")).toHaveLength(2);
    expect(screen.queryByText("Thumbnail unavailable")).toBeNull();
  });
});
