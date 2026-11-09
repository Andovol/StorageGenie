import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { ExpiryPage } from "./ExpiryPage";
import { HouseholdProvider } from "../hooks/HouseholdContext";
import type { AnalyticsSummary, ExpiryStatusResponse, ReminderListResponse } from "../api/types";

const mocks = vi.hoisted(() => ({
  household: { id: "hh-272", name: "SG-272 home", created_at: "2026-01-01" },
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

const statusBody: ExpiryStatusResponse = {
  household_id: mocks.household.id,
  as_of: "2026-09-24",
  category: null,
  rows: [],
  summary: { by_tier: {}, by_bucket: {}, unresolved: 1, total: 1, dateless: 1 },
  unresolved_rows: [{ asset_id: "missing-272", reason: "needs_evidence" }],
};

const remindersBody: ReminderListResponse = { household_id: mocks.household.id, unread_count: 0, items: [] };

const summaryBody: AnalyticsSummary = {
  household_id: mocks.household.id,
  as_of_date: "2026-09-24",
  generated_at: "2026-09-24T00:00:00+00:00",
  assets: { total: 1, active: 1, by_status: {} },
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

describe("ExpiryPage SG-272 G0b I2", () => {
  test("the quiet dateless count renders at body size, not 12 px", async () => {
    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <HouseholdProvider>
          <MemoryRouter>
            <ExpiryPage />
          </MemoryRouter>
        </HouseholdProvider>
      </QueryClientProvider>
    );
    const note = await screen.findByText(/set to need no date/);
    expect(note).toHaveStyle({ fontSize: "13px" });
  });
});
