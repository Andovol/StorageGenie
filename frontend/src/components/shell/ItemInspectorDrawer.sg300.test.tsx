import { describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ItemInspectorDrawer } from "./ItemInspectorDrawer";
import type { Asset } from "../../api/types";

const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPatch: vi.fn(),
  markGone: vi.fn(),
  putBack: vi.fn(),
  decrementQuantity: vi.fn(),
  incrementQuantity: vi.fn(),
}));
vi.mock("../../api/client", () => api);
vi.mock("../../hooks/useAssets", () => ({ useTaxonomy: () => ({ data: { plugins: [] } }) }));

function asset(overrides: Partial<Asset> = {}): Asset {
  return {
    id: "asset-300",
    household_id: "h1",
    display_name: "Milk",
    asset_type: "product",
    status: "ACTIVE",
    gone_reason: null,
    quantity: 1,
    unit: "pcs",
    condition: null,
    version: 1,
    created_at: "2026-09-10T00:00:00Z",
    updated_at: null,
    evidence: [],
    assertions: [],
    ...overrides,
  };
}

function renderDrawer(item: Asset) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ItemInspectorDrawer asset={item} householdId="h1" onClose={vi.fn()} />
    </QueryClientProvider>
  );
}

describe("ItemInspectorDrawer SG-300 shared quantity wording", () => {
  test("a counted item reads 1 left, never 1 pcs left", async () => {
    api.apiGet.mockImplementation((path: string) =>
      path.includes("/v1/assets/") ? Promise.resolve(asset()) : Promise.resolve({ plugins: [] })
    );
    renderDrawer(asset({ quantity: 1, unit: "pcs" }));
    expect(await screen.findByText("1 left")).toBeInTheDocument();
    expect(screen.queryByText(/pcs left/)).toBeNull();
  });

  test("an amount item reads 340 g left", async () => {
    api.apiGet.mockImplementation((path: string) =>
      path.includes("/v1/assets/")
        ? Promise.resolve(asset({ quantity: 340, unit: "g" }))
        : Promise.resolve({ plugins: [] })
    );
    renderDrawer(asset({ quantity: 340, unit: "g" }));
    expect(await screen.findByText(/^340 g left/)).toBeInTheDocument();
  });
});
