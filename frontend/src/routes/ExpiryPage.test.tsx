import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { ExpiryPage } from "./ExpiryPage";
import type { AnalyticsSummary, ExpiryStatusResponse } from "../api/types";

// Fixtures are hoisted so the `vi.mock` factory below can close over them
// without a temporal-dead-zone race against the hoisted mock call.
const mocks = vi.hoisted(() => ({
  household: { id: "hh-expiry", name: "Expiry home", created_at: "2026-01-01" },
  taxonomy: {
    plugins: [
      {
        plugin_id: "expiry-tracker",
        version: "1.0.0",
        categories: [
          { id: "food_beverages", name: "Food & beverages", active: true, notification: "tiered-30-7-1", opened_date_tracking: false, chat: "category" },
          { id: "medicine_pharma", name: "Medicine/pharma", active: true, notification: "tiered-short", opened_date_tracking: false, chat: "category" },
          { id: "documents_other", name: "Documents/other", active: true, notification: "long-lead-60-30", opened_date_tracking: false, chat: "fallback" },
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

const household = mocks.household;

// The response mirrors the SG-107 engine route keys exactly.
const statusFixture: ExpiryStatusResponse = {
  household_id: household.id,
  as_of: "2026-09-24",
  category: null,
  rows: [
    { asset_id: "a1", display_name: "Milk", category: "food_beverages", expiry_date: "2026-09-20", date_type: "use_by", days_remaining: -4, tier: null, bucket: "expired" },
    { asset_id: "a2", display_name: "Yogurt", category: "food_beverages", expiry_date: "2026-09-27", date_type: "best_before", days_remaining: 3, tier: "urgent", bucket: "this-week" },
    { asset_id: "a5", display_name: "Soap", category: "cosmetics_personal_care", expiry_date: "2026-10-01", date_type: "expiry_date", days_remaining: 7, tier: "critical", bucket: "this-week" },
    { asset_id: "a3", display_name: "Aspirin", category: "medicine_pharma", expiry_date: "2026-10-10", date_type: "use_by", days_remaining: 16, tier: "upcoming", bucket: "this-month" },
    { asset_id: "a7", display_name: "Passport", category: "documents_other", expiry_date: "2026-11-08", date_type: "expiry_date", days_remaining: 45, tier: "long_lead", bucket: "safe" },
    { asset_id: "a4", display_name: "Warranty", category: "documents_other", expiry_date: "2027-06-01", date_type: "expiry_date", days_remaining: 250, tier: "safe", bucket: "safe" },
    { asset_id: "a6", display_name: "Batteries", category: "non_perishable", expiry_date: "2026-12-01", date_type: "expiry_date", days_remaining: 68, tier: null, bucket: "safe" },
  ],
  summary: {
    by_tier: { none: 2, urgent: 1, critical: 1, upcoming: 1, long_lead: 1, safe: 1 },
    by_bucket: { expired: 1, "this-week": 2, "this-month": 1, safe: 3 },
    unresolved: 4,
    total: 11,
  },
  unresolved_rows: [
    { asset_id: "u1", reason: "proposed" },
    { asset_id: "u2", reason: "needs_evidence" },
    { asset_id: "u3", reason: "unparseable" },
    { asset_id: "u4", reason: "dateless" },
  ],
};

const emptyFixture: ExpiryStatusResponse = {
  household_id: household.id,
  as_of: "2026-09-24",
  category: null,
  rows: [],
  summary: { by_tier: {}, by_bucket: {}, unresolved: 0, total: 0 },
  unresolved_rows: [],
};

const summaryFixture: AnalyticsSummary = {
  household_id: household.id,
  as_of_date: "2026-09-24",
  generated_at: "2026-09-24T00:00:00+00:00",
  assets: { total: 6, active: 6, by_status: {} },
  categories: {
    taxonomy: [
      { id: "food_beverages", name: "Food & beverages" },
      { id: "medicine_pharma", name: "Medicine/pharma" },
    ],
    counts: {},
    uncategorized: 6,
  },
  expiry: {},
  waste: { expired_untouched: 0 },
  adherence: { suggestions: {}, review_tasks: {} },
  stats: [],
};

function jsonResponse(body: unknown): Response {
  return { ok: true, json: async () => body } as Response;
}

let statusBody: ExpiryStatusResponse;
let fetchMock = vi.fn((input: RequestInfo | URL): Promise<Response> => {
  void input;
  return Promise.resolve(jsonResponse({}));
});

beforeEach(() => {
  localStorage.clear();
  statusBody = statusFixture;
  fetchMock = vi.fn((input: RequestInfo | URL): Promise<Response> => {
    const url = String(input);
    if (url.includes("/v1/plugins/expiry-tracker/status")) {
      return Promise.resolve(jsonResponse(statusBody));
    }
    if (url.includes("/v1/analytics/summary")) {
      return Promise.resolve(jsonResponse(summaryFixture));
    }
    return Promise.resolve(jsonResponse({}));
  });
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>
        <ExpiryPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

function calledUrls(): string[] {
  return fetchMock.mock.calls.map((call) => String(call[0]));
}

describe("ExpiryPage", () => {
  test("reads the SG-107 engine route with the household (and no category by default)", async () => {
    renderPage();
    await screen.findByText("Milk");

    await waitFor(() =>
      expect(
        calledUrls().some(
          (url) => url.includes("/v1/plugins/expiry-tracker/status") && url.includes("household_id=hh-expiry")
        )
      ).toBe(true)
    );
    expect(calledUrls().some((url) => url.includes("category="))).toBe(false);
  });

  test("renders the urgency sections in blueprint order with exact labels", async () => {
    renderPage();
    await screen.findByText("Milk");

    expect(screen.getAllByRole("region").map((region) => region.getAttribute("aria-label"))).toEqual([
      "Expired",
      "This week",
      "This month",
      "Safe",
      "Unresolved",
      "Uncategorized",
    ]);
    expect(within(screen.getByRole("region", { name: "Expired" })).getByText("4 days overdue")).toBeInTheDocument();
    expect(within(screen.getByRole("region", { name: "This week" })).getByText("3 days remaining")).toBeInTheDocument();
  });

  test("maps every tier to its pill label including No tier", async () => {
    renderPage();
    await screen.findByText("Milk");

    const pills = screen.getAllByTestId("tier-pill").map((pill) => pill.textContent);
    expect(pills).toEqual(expect.arrayContaining(["Critical", "Urgent", "Upcoming", "Long lead", "Safe", "No tier"]));
  });

  test("labels every unresolved reason", async () => {
    renderPage();
    await screen.findByText("Milk");

    const unresolved = screen.getByRole("region", { name: "Unresolved" });
    for (const label of ["Proposed", "Needs evidence", "Unparseable date", "No date"]) {
      expect(within(unresolved).getByText(label)).toBeInTheDocument();
    }
  });

  test("links each row to the asset route with the household scoping", async () => {
    renderPage();
    await screen.findByText("Milk");

    expect(screen.getByRole("link", { name: "Milk" })).toHaveAttribute(
      "href",
      "/assets/a1?household_id=hh-expiry"
    );
  });

  test("passes the category filter through to the engine request", async () => {
    renderPage();
    await screen.findByText("Milk");

    fireEvent.change(screen.getByLabelText("Category filter"), { target: { value: "food_beverages" } });

    await waitFor(() =>
      expect(calledUrls().some((url) => url.includes("category=food_beverages"))).toBe(true)
    );
  });

  test("renders the empty state for an empty-zeroed engine body", async () => {
    statusBody = emptyFixture;
    renderPage();

    expect(await screen.findByText("No expiry items for this household.")).toBeInTheDocument();
  });

  test("shows the uncategorized line sourced from the served summary", async () => {
    renderPage();
    await screen.findByText("Milk");

    const uncategorized = await screen.findByRole("region", { name: "Uncategorized" });
    expect(within(uncategorized).getByText("6")).toBeInTheDocument();
    expect(calledUrls().some((url) => url.includes("/v1/analytics/summary"))).toBe(true);
  });
});
