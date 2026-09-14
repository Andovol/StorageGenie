import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HouseholdSelector } from "./HouseholdSelector";
import type { Household } from "../api/types";

const mockHouseholds: Household[] = [
  { id: "hh-1", name: "Main Home", created_at: "2026-01-01" },
  { id: "hh-2", name: "Vacation Home", created_at: "2026-01-01" },
];

describe("HouseholdSelector", () => {
  it("renders label and select options correctly", () => {
    const handleChange = vi.fn();
    render(
      <HouseholdSelector
        value="hh-1"
        onChange={handleChange}
        households={mockHouseholds}
      />
    );

    expect(screen.getByLabelText(/Household/i)).toBeInTheDocument();
    expect(screen.getByRole("combobox")).toHaveValue("hh-1");
    expect(screen.getByText("Select household")).toBeInTheDocument();
    expect(screen.getByText("Main Home")).toBeInTheDocument();
    expect(screen.getByText("Vacation Home")).toBeInTheDocument();
  });

  it("calls onChange when selection changes", () => {
    const handleChange = vi.fn();
    render(
      <HouseholdSelector
        value="hh-1"
        onChange={handleChange}
        households={mockHouseholds}
      />
    );

    fireEvent.change(screen.getByRole("combobox"), { target: { value: "hh-2" } });
    expect(handleChange).toHaveBeenCalledWith("hh-2");
  });

  it("supports hiding the label wrapper and custom empty option label", () => {
    const handleChange = vi.fn();
    const { container } = render(
      <HouseholdSelector
        value=""
        onChange={handleChange}
        households={mockHouseholds}
        showLabel={false}
        emptyOptionLabel="No selection"
      />
    );

    expect(container.querySelector("label")).toBeNull();
    expect(screen.getByRole("combobox")).toBeInTheDocument();
    expect(screen.getByText("No selection")).toBeInTheDocument();
  });
});
