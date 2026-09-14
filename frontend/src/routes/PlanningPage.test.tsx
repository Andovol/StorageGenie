import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { PlanningPage } from "./PlanningPage";
import type { PlanningSuggestion } from "../api/types";

const household = { id: "hh-planning", name: "Planning home", created_at: "2026-01-01" };

const suggestion: PlanningSuggestion = {
  id: "sug-planning-1",
  household_id: household.id,
  kind: "use_first",
  title: 'Use "Whole milk" before 2026-09-16',
  body: { rationale: ["expires soon"], confidence: 1.0 },
  backing_refs: [{ type: "asset", id: "asset-9", label: "Whole milk", category: "food_beverages" }],
  status: "pending",
  created_at: null,
  updated_at: null,
};

const api = vi.hoisted(() => ({
  runPlanning: vi.fn(),
  fetchPlanningSuggestions: vi.fn(),
  confirmPlanningSuggestion: vi.fn(),
  dismissPlanningSuggestion: vi.fn(),
}));
vi.mock("../api/client", () => api);
vi.mock("../hooks/useAssets", () => ({ useHouseholds: () => ({ data: [household] }) }));

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <PlanningPage />
    </QueryClientProvider>
  );
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("PlanningPage", () => {
  test("running planning posts and a pending suggestion appears", async () => {
    api.fetchPlanningSuggestions
      .mockResolvedValueOnce({ items: [], total: 0 })
      .mockResolvedValue({ items: [suggestion], total: 1 });
    api.runPlanning.mockResolvedValue({
      status: "ok",
      suggestion_count: 1,
      catalog_size: 1,
      provider: "scripted-plan",
      model: "scripted-plan-1",
    });
    renderPage();
    expect(await screen.findByText("No planning suggestions yet.")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Run planning" }));

    await waitFor(() => expect(api.runPlanning).toHaveBeenCalledWith(household.id));
    expect(await screen.findByText(suggestion.title)).toBeInTheDocument();
    expect(await screen.findByText("Planning wrote 1 suggestion(s).")).toBeInTheDocument();
  });

  test("confirm and dismiss round-trip against the loaded suggestion id", async () => {
    api.fetchPlanningSuggestions.mockResolvedValue({ items: [suggestion], total: 1 });
    api.confirmPlanningSuggestion.mockResolvedValue({ ...suggestion, status: "confirmed" });
    api.dismissPlanningSuggestion.mockResolvedValue({ ...suggestion, status: "dismissed" });
    renderPage();
    await screen.findByText(suggestion.title);

    fireEvent.click(screen.getByRole("button", { name: "Confirm" }));
    await waitFor(() =>
      expect(api.confirmPlanningSuggestion).toHaveBeenCalledWith(suggestion.id, household.id)
    );

    fireEvent.click(screen.getByRole("button", { name: "Dismiss" }));
    await waitFor(() =>
      expect(api.dismissPlanningSuggestion).toHaveBeenCalledWith(suggestion.id, household.id)
    );
  });

  test("a refused run surfaces the reason", async () => {
    api.fetchPlanningSuggestions.mockResolvedValue({ items: [], total: 0 });
    api.runPlanning.mockResolvedValue({
      status: "skipped",
      reason: "consent_disabled",
      suggestion_count: 0,
      catalog_size: 1,
    });
    renderPage();
    await screen.findByText("No planning suggestions yet.");

    fireEvent.click(screen.getByRole("button", { name: "Run planning" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Planning did not run: consent_disabled"
    );
  });

  test("the status filter refetches with the chosen status", async () => {
    api.fetchPlanningSuggestions.mockResolvedValue({ items: [], total: 0 });
    renderPage();
    await screen.findByText("No planning suggestions yet.");

    fireEvent.change(screen.getByLabelText("Status"), { target: { value: "confirmed" } });

    await waitFor(() =>
      expect(api.fetchPlanningSuggestions).toHaveBeenCalledWith(household.id, "confirmed")
    );
  });
});
