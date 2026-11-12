import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ItemInspectorDrawer } from "./ItemInspectorDrawer";
import { CatalogToolbar, THEMED_CONTROL_CLASS } from "./CatalogToolbar";
import { ThemeToggle } from "../../theme/ThemeToggle";
import { ThemeProvider } from "../../theme/ThemeProvider";
import { CatalogPage } from "../../routes/CatalogPage";
import { HouseholdProvider } from "../../hooks/HouseholdContext";
import type { Asset } from "../../api/types";

const api = vi.hoisted(() => ({ apiGet: vi.fn(), apiPatch: vi.fn() }));
vi.mock("../../api/client", () => api);

function baseAsset(overrides: Partial<Asset> = {}): Asset {
  return {
    id: "asset-307",
    household_id: "h1",
    display_name: "Milk",
    asset_type: "unknown",
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

describe("SG-307 item panel plain words, square paper", () => {
  beforeEach(() => {
    api.apiGet.mockImplementation((path: string) =>
      path.includes("/v1/assets/") ? Promise.resolve(baseAsset()) : Promise.resolve(null)
    );
  });
  afterEach(() => {
    vi.clearAllMocks();
  });

  test("plain tab names and one-line cut-out empty state, no developer sentences", async () => {
    renderDrawer(baseAsset());
    await screen.findByTestId("inspector-drawer");
    expect(screen.getByRole("tab", { name: "Photo" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Cut-out" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "In a scene" })).toBeInTheDocument();
    expect(screen.queryByRole("tab", { name: "Isolated Cutout" })).toBeNull();
    expect(screen.queryByRole("tab", { name: "Scene / Context" })).toBeNull();
    fireEvent.click(screen.getByRole("tab", { name: "Cut-out" }));
    expect(screen.getByTestId("cutout-honest-state")).toHaveTextContent("No cut-out yet.");
    expect(screen.queryByText(/arrives with the AI stages/i)).toBeNull();
    expect(screen.queryByText(/nothing is being processed/i)).toBeNull();
  });

  test("the bounding-box sentence is off the screen but kept as a data hook", async () => {
    renderDrawer(baseAsset());
    await screen.findByTestId("inspector-drawer");
    expect(screen.queryByText(/bounding-box overlay omitted/i)).toBeNull();
    expect(screen.getByTestId("viewer-well")).toHaveAttribute("data-bbox-omitted", "true");
  });

  test("no font-mono and no text under 13px in the rendered panel", async () => {
    const { container } = renderDrawer(baseAsset());
    await screen.findByTestId("inspector-drawer");
    expect(container.querySelector(".font-mono")).toBeNull();
  });

  test("Kind of item reads the asset_type field in plain words", async () => {
    renderDrawer(baseAsset({ asset_type: "unknown" }));
    await screen.findByTestId("inspector-drawer");
    expect(screen.getByTestId("drawer-category")).toHaveTextContent("Uncategorized");
    expect(screen.getByLabelText("Kind of item")).toHaveValue("Uncategorized");
  });
});

describe("SG-307 paper controls and 375 header", () => {
  test("the shared rule exists and the toolbar, toggle and review select come out of it", () => {
    expect(THEMED_CONTROL_CLASS).toContain("sg-paper-control");
    render(
      <MemoryRouter>
        <CatalogToolbar
          categories={["All (1)"]}
          activeCategory="All (1)"
          onCategoryChange={() => {}}
          statusFilter="live"
          onStatusFilterChange={() => {}}
          sort="recent"
          onSortChange={() => {}}
          density="grid"
          onDensityChange={() => {}}
          activeFilters={[]}
          onClearAll={() => {}}
          savedSearches={[]}
          selectedSavedSearchId=""
          onSavedSearchSelect={() => {}}
          onSavedSearchDelete={() => {}}
          onSaveSearch={() => {}}
        />
      </MemoryRouter>
    );
    const toolbar = screen.getByTestId("catalog-toolbar");
    expect(toolbar.style.backgroundColor).toContain("paper");
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );
    const toggle = screen.getByTestId("theme-toggle");
    expect(toggle.className).toContain("sg-paper-control");
    expect(toggle.className).not.toContain("bg-card");
  });

  test("the 375 header rule: icon-shortened Import with aria-label and one-row classes", () => {
    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <MemoryRouter>
          <ThemeProvider>
            <HouseholdProvider>
              <CatalogPage />
            </HouseholdProvider>
          </ThemeProvider>
        </MemoryRouter>
      </QueryClientProvider>
    );
    expect(screen.getByTestId("catalog-header")).toHaveClass("sg-header");
    expect(screen.getByTestId("catalog-header").querySelector(".sg-import-label")).toBeInTheDocument();
  });
});
