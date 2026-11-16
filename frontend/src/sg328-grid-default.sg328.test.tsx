import { beforeEach, afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "./theme/ThemeProvider";
import { HouseholdProvider } from "./hooks/HouseholdContext";
import { CatalogPage } from "./routes/CatalogPage";
import type { Asset } from "./api/types";

const api = vi.hoisted(() => ({ apiGet: vi.fn(), apiPatch: vi.fn() }));
vi.mock("./api/client", () => api);

// SG-328: shape copied from components/catalog/catalog.test.tsx drawer-wiring
// asset (the shape the API sends).
const catalogAsset: Asset = {
  id: "a-drill",
  household_id: "h1",
  display_name: "Drill",
  asset_type: "Hardware & Tools",
  status: "ACTIVE",
  quantity: null,
  unit: null,
  condition: null,
  version: 1,
  created_at: "2026-09-10T00:00:00Z",
  updated_at: null,
};

function mockCatalogApi() {
  api.apiGet.mockImplementation((path: string) => {
    if (path === "/v1/households") {
      return Promise.resolve([{ id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" }]);
    }
    if (path === "/v1/assets/facets") {
      return Promise.resolve({
        asset_type: { "Hardware & Tools": 1 },
        status: { ACTIVE: 1 },
        has_evidence: { with: 0, without: 1 },
      });
    }
    if (path === "/v1/assets") {
      return Promise.resolve({ items: [catalogAsset], next_cursor: null });
    }
    return Promise.resolve(null);
  });
}

// jsdom lays nothing out, so clientWidth is 0 for every element. Mock the
// content-column read to simulate wide/narrow mounts (SG-212 helper, kept so
// the SG-328 tests prove the width no longer matters).
function mockContentColumnWidth(width: number) {
  const spy = vi.spyOn(Element.prototype, "clientWidth", "get");
  spy.mockImplementation(function (this: Element) {
    return this instanceof HTMLElement &&
      this.getAttribute("data-testid") === "catalog-content-column"
      ? width
      : 0;
  });
  return spy;
}

function renderCatalog() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ThemeProvider>
        <MemoryRouter initialEntries={["/"]}>
          <HouseholdProvider>
            <CatalogPage />
          </HouseholdProvider>
        </MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

describe("SG-328 catalog grid default", () => {
  beforeEach(() => {
    window.localStorage.clear();
    api.apiGet.mockReset();
    api.apiPatch.mockReset();
    mockCatalogApi();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("a wide content column (1280 px) opens in Standard Grid", async () => {
    mockContentColumnWidth(1280);
    renderCatalog();

    expect(screen.getByRole("button", { name: "Standard Grid" })).toHaveAttribute(
      "aria-pressed",
      "true"
    );
    expect(screen.getByRole("button", { name: "Compact Table" })).toHaveAttribute(
      "aria-pressed",
      "false"
    );

    await screen.findByTestId("product-card");
    expect(screen.getByTestId("catalog-grid")).toBeInTheDocument();
    expect(screen.queryByTestId("table-scroll")).not.toBeInTheDocument();
  });

  test("a narrow content column (320 px) opens in Standard Grid", async () => {
    mockContentColumnWidth(320);
    renderCatalog();

    expect(screen.getByRole("button", { name: "Standard Grid" })).toHaveAttribute(
      "aria-pressed",
      "true"
    );

    await screen.findByTestId("product-card");
    expect(screen.getByTestId("catalog-grid")).toBeInTheDocument();
    expect(screen.queryByTestId("table-scroll")).not.toBeInTheDocument();
  });

  test("Compact Table still switches to the table and back", async () => {
    mockContentColumnWidth(1280);
    renderCatalog();
    await screen.findByTestId("product-card");

    fireEvent.click(screen.getByRole("button", { name: "Compact Table" }));
    expect(screen.getByRole("button", { name: "Compact Table" })).toHaveAttribute(
      "aria-pressed",
      "true"
    );
    await screen.findByTestId("product-row");
    expect(screen.getByTestId("table-scroll")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Standard Grid" }));
    expect(screen.getByRole("button", { name: "Standard Grid" })).toHaveAttribute(
      "aria-pressed",
      "true"
    );
    await screen.findByTestId("product-card");
    expect(screen.queryByTestId("table-scroll")).not.toBeInTheDocument();
  });
});
