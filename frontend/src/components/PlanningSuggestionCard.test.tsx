import { describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { PlanningSuggestionCard } from "./PlanningSuggestionCard";
import type { PlanningSuggestion } from "../api/types";

const suggestion: PlanningSuggestion = {
  id: "sug-1",
  household_id: "hh-1",
  kind: "use_first",
  title: 'Use "Whole milk" before 2026-09-16',
  body: { rationale: ["expires soon"], confidence: 1.0 },
  backing_refs: [
    { type: "asset", id: "asset-1", label: "Whole milk", category: "food_beverages" },
    {
      type: "assertion",
      id: "assert-1",
      field_path: "plugin:expiry-tracker/expiry_date",
      value: "2026-09-16",
    },
  ],
  status: "pending",
  created_at: null,
  updated_at: null,
};

describe("PlanningSuggestionCard", () => {
  test("renders title, status, rationale and backing evidence", () => {
    render(
      <PlanningSuggestionCard suggestion={suggestion} onConfirm={() => {}} onDismiss={() => {}} />
    );
    expect(screen.getByText('Use "Whole milk" before 2026-09-16')).toBeInTheDocument();
    expect(screen.getByText("use_first · pending")).toBeInTheDocument();
    expect(screen.getByText("expires soon")).toBeInTheDocument();
    expect(screen.getByText("[asset: Whole milk]")).toBeInTheDocument();
    expect(
      screen.getByText("[assertion: plugin:expiry-tracker/expiry_date]")
    ).toBeInTheDocument();
  });

  test("confirm/dismiss call back with the loaded id and vanish when not pending", () => {
    const onConfirm = vi.fn();
    const onDismiss = vi.fn();
    const { rerender } = render(
      <PlanningSuggestionCard suggestion={suggestion} onConfirm={onConfirm} onDismiss={onDismiss} />
    );
    fireEvent.click(screen.getByRole("button", { name: "Confirm" }));
    fireEvent.click(screen.getByRole("button", { name: "Dismiss" }));
    expect(onConfirm).toHaveBeenCalledWith("sug-1");
    expect(onDismiss).toHaveBeenCalledWith("sug-1");

    rerender(
      <PlanningSuggestionCard
        suggestion={{ ...suggestion, status: "confirmed" }}
        onConfirm={onConfirm}
        onDismiss={onDismiss}
      />
    );
    expect(screen.queryByRole("button", { name: "Confirm" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Dismiss" })).toBeNull();
  });
});
