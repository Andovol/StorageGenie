import { describe, test, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EvidenceGallery } from "./EvidenceGallery";

describe("EvidenceGallery", () => {
  test("renders empty message when no evidence provided", () => {
    render(<EvidenceGallery evidence={[]} householdId="hh_1" />);
    expect(screen.getByText("No evidence attached")).toBeInTheDocument();
  });

  test("renders evidence links with accessible labels and attributes", () => {
    const mockEvidence = [
      {
        id: "ev_1",
        storage_key: "keys/1",
        original_filename: "receipt.jpg",
        sha256: "abc123sha",
      },
      {
        id: "ev_2",
        storage_key: "keys/2",
      },
    ];

    render(<EvidenceGallery evidence={mockEvidence} householdId="hh_1" />);

    const link1 = screen.getByRole("link", { name: "View evidence file: receipt.jpg (opens in new tab)" });
    expect(link1).toBeInTheDocument();
    expect(link1).toHaveAttribute("target", "_blank");
    expect(link1).toHaveAttribute("rel", "noreferrer");
    expect(link1).toHaveAttribute("title", "SHA256: abc123sha");
    expect(link1).toHaveClass("focus-ring");

    const img1 = screen.getByAltText("Evidence thumbnail for receipt.jpg");
    expect(img1).toBeInTheDocument();

    const link2 = screen.getByRole("link", { name: "View evidence file: ev_2 (opens in new tab)" });
    expect(link2).toBeInTheDocument();

    const img2 = screen.getByAltText("Evidence thumbnail ev_2");
    expect(img2).toBeInTheDocument();
  });

  test("renders fallback text when thumbnail image errors", () => {
    const mockEvidence = [
      {
        id: "ev_err",
        storage_key: "keys/err",
        original_filename: "broken.png",
      },
    ];

    render(<EvidenceGallery evidence={mockEvidence} householdId="hh_1" />);

    const img = screen.getByAltText("Evidence thumbnail for broken.png");
    fireEvent.error(img);

    expect(screen.getByText("Thumbnail unavailable")).toBeInTheDocument();
  });
});
