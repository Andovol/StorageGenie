import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ItemInspectorDrawer } from "./ItemInspectorDrawer";
import type { Asset, Assertion } from "../../api/types";

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

function assertion(
  id: string,
  field_path: string,
  value: unknown,
  review_state = "accepted"
): Assertion {
  return {
    id,
    field_path,
    value,
    source_type: "user",
    review_state,
    confidence: null,
    source_evidence_ids: [],
    created_at: null,
  };
}

function asset(overrides: Partial<Asset> = {}): Asset {
  return {
    id: "asset-272",
    household_id: "h1",
    display_name: "Milk",
    asset_type: "product",
    status: "ACTIVE",
    gone_reason: null,
    quantity: 3,
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

beforeEach(() => {
  api.apiGet.mockImplementation((path: string) => {
    if (path.includes("/v1/assets/")) return Promise.resolve(asset());
    return Promise.resolve({ plugins: [] });
  });
});

afterEach(() => {
  vi.clearAllMocks();
});

describe("ItemInspectorDrawer SG-272", () => {
  test("one tap takes off 1 on a counted item", async () => {
    api.decrementQuantity.mockResolvedValue(asset({ quantity: 2 }));
    renderDrawer(asset({ quantity: 3, unit: "pcs" }));
    fireEvent.click(await screen.findByRole("button", { name: "Take off 1" }));
    await waitFor(() => expect(api.decrementQuantity).toHaveBeenCalledWith("asset-272", "h1"));
  });

  test("an amount item takes a quick edit instead of −1", async () => {
    renderDrawer(asset({ quantity: 500, unit: "ml" }));
    expect(await screen.findByText(/change the amount with Save changes above/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Take off 1" })).toBeNull();
  });

  test("at 0 the panel reads None left", async () => {
    renderDrawer(asset({ quantity: 0, unit: "" }));
    expect(await screen.findByText("None left — mark it gone below.")).toBeInTheDocument();
  });

  test("Mark gone with a reason, then Put back on the gone item", async () => {
    api.markGone.mockResolvedValue(asset({ status: "ARCHIVED", gone_reason: "thrown_away" }));
    renderDrawer(asset({}));
    fireEvent.click(await screen.findByRole("button", { name: "Thrown away" }));
    await waitFor(() => expect(api.markGone).toHaveBeenCalledWith("asset-272", "h1", "thrown_away"));

    api.putBack.mockResolvedValue(asset({ status: "ACTIVE", gone_reason: null }));
    renderDrawer(
      asset({
        status: "ARCHIVED",
        gone_reason: "thrown_away",
        assertions: [assertion("g1", "gone.reason", { reason: "thrown_away" })],
      })
    );
    expect(await screen.findByText("Gone — thrown away")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Put back" }));
    await waitFor(() => expect(api.putBack).toHaveBeenCalledWith("asset-272", "h1"));
  });
});
