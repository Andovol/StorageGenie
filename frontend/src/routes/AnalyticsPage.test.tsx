import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AnalyticsPage } from "./AnalyticsPage";
import type { AnalyticsSummary } from "../api/types";

const household = { id: "hh-analytics", name: "Analytics home", created_at: "2026-01-01" };

const summary: AnalyticsSummary = {
  household_id: household.id,
  as_of_date: "2026-09-21",
  generated_at: "2026-09-21T00:00:00+00:00",
  assets: { total: 4, active: 4, by_status: { ACTIVE: 4 } },
  categories: {
    taxonomy: [
      { id: "food_beverages", name: "Food & beverages" },
      { id: "medicine_pharma", name: "Medicine/pharma" },
    ],
    counts: { food_beverages: 3, medicine_pharma: 1 },
    uncategorized: 0,
  },
  expiry: { expired: 2, within_7_days: 1, within_30_days: 1, safe: 0, unknown: 0 },
  waste: { expired_untouched: 2 },
  adherence: { suggestions: { pending: 5, confirmed: 1, dismissed: 0 }, review_tasks: { open: 2, resolved: 3 } },
  stats: [
    { id: "assets.active", label: "Active assets", value: 4, source: "asset: count(*)" },
    { id: "waste.expired_untouched", label: "Expired assets still active", value: 2, source: "asset + assertion" },
  ],
};

const emptySummary: AnalyticsSummary = {
  ...summary,
  assets: { total: 0, active: 0, by_status: {} },
  categories: { ...summary.categories, counts: { food_beverages: 0, medicine_pharma: 0 } },
  expiry: { expired: 0, within_7_days: 0, within_30_days: 0, safe: 0, unknown: 0 },
  waste: { expired_untouched: 0 },
  adherence: { suggestions: { pending: 0, confirmed: 0, dismissed: 0 }, review_tasks: { open: 0, resolved: 0 } },
};

const api = vi.hoisted(() => ({
  fetchAnalyticsSummary: vi.fn(),
  generateAnalyticsInsights: vi.fn(),
}));
vi.mock("../api/client", () => api);
vi.mock("../hooks/useAssets", () => ({ useHouseholds: () => ({ data: [household] }) }));

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <AnalyticsPage />
    </QueryClientProvider>
  );
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("AnalyticsPage", () => {
  test("renders the endpoint values, not a hardcoded list", async () => {
    api.fetchAnalyticsSummary.mockResolvedValue(summary);
    renderPage();

    expect(await screen.findByText("Food & beverages")).toBeInTheDocument();
    expect(screen.getByText("Medicine/pharma")).toBeInTheDocument();
    expect(screen.getByText("Expired still active")).toBeInTheDocument();
    expect(screen.getByLabelText("Expiry urgency")).toHaveTextContent("Expired2");
    expect(screen.queryByText("No analytics data yet for this household.")).not.toBeInTheDocument();
  });

  test("asserts the empty state for a household with no data", async () => {
    api.fetchAnalyticsSummary.mockResolvedValue(emptySummary);
    renderPage();

    expect(
      await screen.findByText("No analytics data yet for this household.")
    ).toBeInTheDocument();
  });

  test("generate summary posts and renders the prose with its cited stats", async () => {
    api.fetchAnalyticsSummary.mockResolvedValue(summary);
    api.generateAnalyticsInsights.mockResolvedValue({
      status: "ok",
      summary: "Two active assets are already expired.",
      sentences: ["Two active assets are already expired."],
      cited_stat_ids: ["waste.expired_untouched"],
      cited_stats: [
        { id: "waste.expired_untouched", label: "Expired assets still active", value: 2, source: "asset + assertion" },
      ],
    });
    renderPage();
    await screen.findByText("Food & beverages");

    fireEvent.click(screen.getByRole("button", { name: "Generate summary" }));

    await waitFor(() =>
      expect(api.generateAnalyticsInsights).toHaveBeenCalledWith(household.id)
    );
    expect(
      await screen.findByText("Two active assets are already expired.")
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Generated summary")).toHaveTextContent(
      "Expired assets still active: 2"
    );
  });

  test("an ungrounded refusal surfaces the error", async () => {
    api.fetchAnalyticsSummary.mockResolvedValue(summary);
    api.generateAnalyticsInsights.mockRejectedValue(
      new Error("insight cites unknown stat id(s): expiry.bogus")
    );
    renderPage();
    await screen.findByText("Food & beverages");

    fireEvent.click(screen.getByRole("button", { name: "Generate summary" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "insight cites unknown stat id(s): expiry.bogus"
    );
  });
});
