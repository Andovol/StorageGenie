import { describe, test, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ProvenanceBadge } from "./ProvenanceBadge";

describe("ProvenanceBadge", () => {
  test("accepted is green", () => {
    render(<ProvenanceBadge state="accepted" />);
    expect(screen.getByText("accepted")).toHaveClass("badge-green");
  });
  test("proposed is amber", () => {
    render(<ProvenanceBadge state="proposed" />);
    expect(screen.getByText("proposed")).toHaveClass("badge-amber");
  });
  test("needs_evidence is grey", () => {
    render(<ProvenanceBadge state="needs_evidence" />);
    expect(screen.getByText("needs_evidence")).toHaveClass("badge-grey");
  });
});
