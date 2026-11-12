import { describe, test, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ProvenanceBadge } from "./ProvenanceBadge";

describe("ProvenanceBadge", () => {
  test("accepted reads Kept and is green", () => {
    render(<ProvenanceBadge state="accepted" />);
    // SG-301 G2: the raw review_state reads as a plain word.
    expect(screen.getByText("Kept")).toHaveClass("badge-green");
  });
  test("proposed reads Suggested and is amber", () => {
    render(<ProvenanceBadge state="proposed" />);
    expect(screen.getByText("Suggested")).toHaveClass("badge-amber");
  });
  test("needs_evidence reads Needs Evidence and is grey", () => {
    render(<ProvenanceBadge state="needs_evidence" />);
    expect(screen.getByText("Needs Evidence")).toHaveClass("badge-grey");
  });
});
