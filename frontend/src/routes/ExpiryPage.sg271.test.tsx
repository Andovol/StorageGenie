import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { ExpiryPage } from "./ExpiryPage";
import { HouseholdProvider } from "../hooks/HouseholdContext";
import type { AnalyticsSummary, ExpiryStatusResponse, ReminderListResponse } from "../api/types";

const mocks = vi.hoisted(() => ({
  household: { id: "hh-271", name: "SG-271 home", created_at: "2026-01-01" },
  taxonomy: {
    plugins: [
      {
        plugin_id: "expiry-tracker",
        version: "1.0.0",
        categories: [
          { id: "food_beverages", name: "Food & beverages", active: true, notification: "tiered-30-7-1", opened_date_tracking: false, chat: "category" },
        ],
        date_types: ["expiry_date", "use_by"],
        units: ["count"],
      },
    ],
  },
}));

vi.mock("../hooks/useAssets", () => ({
  useHouseholds: () => ({ data: [mocks.household] }),
  useTaxonomy: () => ({ data: mocks.taxonomy }),
}));

function jsonResponse(body: unknown): Response {
  return { ok: true, json: async () => body } as Response;
}

// A deliberate dateless item is off Unresolved and counted quietly; a truly
// missing date stays listed; a proposed date reads as proposed, not missing.
const statusBody: ExpiryStatusResponse = {
  household_id: mocks.household.id,
  as_of: "2026-09-24",
  category: null,
  rows: [],
  summary: { by_tier: {}, by_bucket: {}, unresolved: 2, total: 2, dateless: 2 },
  unresolved_rows: [
    { asset_id: "missing-271", reason: "needs_evidence" },
    { asset_id: "proposed-271", reason: "proposed" },
  ],
};

const remindersBody: ReminderListResponse = { household_id: mocks.household.id, unread_count: 0, items: [] };

const summaryBody: AnalyticsSummary = {
  household_id: mocks.household.id,
  as_of_date: "2026-09-24",
  generated_at: "2026-09-24T00:00:00+00:00",
  assets: { total: 4, active: 4, by_status: {} },
  categories: { taxonomy: [], counts: {}, uncategorized: 0 },
  expiry: {},
  waste: { expired_untouched: 0 },
  adherence: { suggestions: {}, review_tasks: {} },
  stats: [],
};

beforeEach(() => {
  localStorage.clear();
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/v1/reminders")) return Promise.resolve(jsonResponse(remindersBody));
      if (url.includes("/v1/plugins/expiry-tracker/opened")) {
        return Promise.resolve(jsonResponse({ household_id: mocks.household.id, as_of: "2026-09-24", rows: [] }));
      }
      if (url.includes("/v1/plugins/expiry-tracker/status")) return Promise.resolve(jsonResponse(statusBody));
      if (url.includes("/v1/analytics/summary")) return Promise.resolve(jsonResponse(summaryBody));
      return Promise.resolve(jsonResponse({}));
    })
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
});

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <HouseholdProvider>
        <MemoryRouter>
          <ExpiryPage />
        </MemoryRouter>
      </HouseholdProvider>
    </QueryClientProvider>
  );
}

describe("ExpiryPage SG-271", () => {
  test("deliberate dateless items stay out of Unresolved with a quiet count", async () => {
    renderPage();
    const section = await screen.findByRole("region", { name: "Unresolved" });
    expect(section.textContent || "").toContain("Unresolved (2)");
    expect(section.textContent || "").toContain("2 items are set to need no date");
    expect(within(section).getByText("Date proposed", { exact: false })).toBeInTheDocument();
  });
});
