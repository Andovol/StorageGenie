import { describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ItemInspectorDrawer } from "./components/shell/ItemInspectorDrawer";

const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPatch: vi.fn(),
  decrementQuantity: vi.fn(),
  incrementQuantity: vi.fn(),
  markGone: vi.fn(),
  putBack: vi.fn(),
}));
vi.mock("./api/client", () => api);
vi.mock("./hooks/useAssets", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./hooks/useAssets")>()),
  useTaxonomy: () => ({ data: { plugins: [] } }),
}));

describe("SG-324 P7 item panel", () => {
  test("cut-out and styled photo read in plain words", () => {
    const asset = {
      id: "a1",
      household_id: "hh",
      display_name: "Milk",
      asset_type: "product",
      status: "ACTIVE",
      quantity: 1,
      unit: "pcs",
      condition: null,
      version: 1,
      created_at: "2026-09-14T00:00:00+00:00",
      updated_at: null,
      evidence: [],
      assertions: [],
    };
    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <ItemInspectorDrawer asset={asset} householdId="hh" onClose={vi.fn()} />
      </QueryClientProvider>
    );
    expect(screen.getByRole("button", { name: /Cut out the item again/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Make a styled photo/ })).toBeInTheDocument();
  });
});
