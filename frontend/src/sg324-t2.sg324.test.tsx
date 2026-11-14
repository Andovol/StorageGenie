import { describe, expect, test, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { OpenedCountdownSection } from "./components/OpenedCountdownSection";

function jsonResponse(body: unknown): Response {
  return { ok: true, json: async () => body } as Response;
}

describe("SG-324 T2 nameless reads Unnamed item", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve(
          jsonResponse({
            household_id: "hh",
            as_of: "2026-10-24",
            rows: [
              {
                asset_id: "a1",
                display_name: null,
                category: "cosmetics_personal_care",
                opened_date: null,
                days_open: null,
                window_months: 12,
                window_source: "category_default",
                days_remaining: null,
                window_end: null,
              },
            ],
          })
        )
      )
    );
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("nameless opened row reads Unnamed item, never Untitled item", async () => {
    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <MemoryRouter>
          <OpenedCountdownSection householdId="hh" />
        </MemoryRouter>
      </QueryClientProvider>
    );
    // CatalogPage gone (routes/CatalogPage.tsx:313) and PantryPage tile
    // (routes/PantryPage.tsx:190) carry the same literal; fixed together and
    // proven by the A6 grep (no Untitled item outside tests).
    expect(await screen.findByText("Unnamed item")).toBeInTheDocument();
    expect(screen.queryByText("Untitled item")).toBeNull();
  });
});
