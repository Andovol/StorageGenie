import { describe, expect, test, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { OpenedCountdownSection } from "./components/OpenedCountdownSection";

function jsonResponse(body: unknown): Response {
  return { ok: true, json: async () => body } as Response;
}

let rows: unknown[];

beforeEach(() => {
  rows = [];
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/v1/plugins/expiry-tracker/opened")) {
        return Promise.resolve(jsonResponse({ household_id: "hh-1", as_of: "2026-10-24", rows }));
      }
      return Promise.resolve(jsonResponse({}));
    })
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
});

function renderSection() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>
        <OpenedCountdownSection householdId="hh-1" />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("SG-324 P5 opened countdown", () => {
  test("empty rows render nothing, not even the heading", async () => {
    rows = [];
    renderSection();
    await screen.findByText("Serum", {}, { timeout: 100 }).catch(() => null);
    await new Promise((resolve) => setTimeout(resolve, 300));
    expect(screen.queryByText("Opened countdown")).toBeNull();
    expect(screen.queryByText("No cosmetics items to track.")).toBeNull();
  });

  test("a row renders the heading and the item", async () => {
    rows = [
      {
        asset_id: "a1",
        display_name: "Serum",
        category: "cosmetics_personal_care",
        opened_date: "2026-01-31",
        days_open: 15,
        window_months: 12,
        window_source: "category_default",
        days_remaining: 350,
        window_end: "2027-01-31",
      },
    ];
    renderSection();
    expect(await screen.findByText("Opened countdown")).toBeInTheDocument();
    expect(await screen.findByText("Serum")).toBeInTheDocument();
  });
});
