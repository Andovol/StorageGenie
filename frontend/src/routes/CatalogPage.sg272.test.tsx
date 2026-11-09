import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "../theme/ThemeProvider";
import { CatalogPage } from "./CatalogPage";

const hooks = vi.hoisted(() => ({ useAssetsImpl: vi.fn() }));
const client = vi.hoisted(() => ({ putBack: vi.fn() }));

vi.mock("../hooks/HouseholdContext", () => ({
  useHouseholdContext: () => ({
    households: [{ id: "hh", name: "Home", created_at: "2026-01-01" }],
    isError: false,
    error: null,
    householdId: "hh",
  }),
}));

vi.mock("../hooks/useAssets", () => ({
  useAssets: (...args: unknown[]) => hooks.useAssetsImpl(...args),
  useFacets: () => ({ data: { asset_type: {}, status: {}, has_evidence: {} }, isError: false, error: null }),
  useSavedSearches: () => ({ data: { items: [] }, isError: false, error: null }),
  useSaveSearch: () => ({ mutate: vi.fn() }),
  useDeleteSavedSearch: () => ({ mutate: vi.fn() }),
  useTaxonomy: () => ({ data: { plugins: [] } }),
}));

vi.mock("../api/client", async (importOriginal) => {
  const original = await importOriginal<typeof import("../api/client")>();
  return { ...original, putBack: (...args: unknown[]) => client.putBack(...args) };
});

const liveItems = [
  {
    id: "live-1",
    household_id: "hh",
    display_name: "Milk",
    asset_type: "product",
    status: "ACTIVE",
    gone_reason: null,
    quantity: 2,
    unit: "pcs",
    condition: null,
    version: 1,
    created_at: "2026-09-14T00:00:00+00:00",
  },
];

const goneItems = [
  {
    id: "gone-1",
    household_id: "hh",
    display_name: "Old Yogurt",
    asset_type: "product",
    status: "ARCHIVED",
    gone_reason: "used_up",
    quantity: 0,
    unit: "pcs",
    condition: null,
    version: 3,
    created_at: "2026-09-10T00:00:00+00:00",
  },
];

// Stable response identities: the page accumulates `data.items` in an effect
// keyed on the `data` reference, so a mock that builds a fresh object per
// render would loop forever (worker OOM). One frozen payload per case.
const liveResp = { items: liveItems, next_cursor: null };
const goneResp = { items: goneItems, next_cursor: null };
const emptyResp = { items: [], next_cursor: null };

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ThemeProvider>
        <MemoryRouter>
          <CatalogPage />
        </MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("CatalogPage SG-272 Gone view", () => {
  test("the Gone toggle asks for ARCHIVED and shows each reason with Put back", async () => {
    hooks.useAssetsImpl.mockImplementation(
      (_hh: string, _q: string, _cursor: string | undefined, _type?: string, status?: string) => ({
        data: status === "ARCHIVED" ? goneResp : liveResp,
        isLoading: false,
        isFetching: false,
        isError: false,
        error: null,
      })
    );
    client.putBack.mockResolvedValue({ ...goneItems[0], status: "ACTIVE", gone_reason: null });
    renderPage();

    fireEvent.click(screen.getByRole("button", { name: "Gone" }));
    expect(await screen.findByText("Old Yogurt")).toBeInTheDocument();
    expect(screen.getByText("Gone — used up")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Put back" }));
    await waitFor(() => expect(client.putBack).toHaveBeenCalledWith("gone-1", "hh"));
  });

  test("an empty Gone view says nothing is gone", async () => {
    hooks.useAssetsImpl.mockImplementation(() => ({
      data: emptyResp,
      isLoading: false,
      isFetching: false,
      isError: false,
      error: null,
    }));
    renderPage();
    fireEvent.click(screen.getByRole("button", { name: "Gone" }));
    expect(await screen.findByText(/Nothing is gone/)).toBeInTheDocument();
  });
});
