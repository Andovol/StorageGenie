import { beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactElement } from "react";
import type { ProductStatus } from "../../types/product";
import type { Asset } from "../../api/types";
import { CatalogPage } from "../../routes/CatalogPage";
import { ThemeProvider } from "../../theme/ThemeProvider";
import { BADGE_CLASS, ProductCard, type CatalogProduct } from "./ProductCard";
import { ProductCardSkeleton } from "./ProductCardSkeleton";
import { ProductGrid, formatRelativeDate } from "./ProductGrid";
import { MOCK_PRODUCTS } from "./mockProducts";

const api = vi.hoisted(() => ({ apiGet: vi.fn(), apiPatch: vi.fn() }));
vi.mock("../../api/client", () => api);

const DQ3_PAIRS: Record<ProductStatus, string[]> = {
  raw: [
    "bg-stone-100",
    "text-stone-700",
    "border-stone-200",
    "dark:bg-stone-800/50",
    "dark:text-stone-400",
    "dark:border-stone-700/50",
  ],
  processed: [
    "bg-sky-50",
    "text-sky-800",
    "border-sky-200",
    "dark:bg-sky-950/40",
    "dark:text-sky-400",
    "dark:border-sky-800/50",
  ],
  rendered: [
    "bg-emerald-50",
    "text-emerald-800",
    "border-emerald-200",
    "dark:bg-emerald-950/40",
    "dark:text-emerald-400",
    "dark:border-emerald-800/50",
  ],
  failed: [
    "bg-rose-50",
    "text-rose-800",
    "border-rose-200",
    "dark:bg-rose-950/40",
    "dark:text-rose-400",
    "dark:border-rose-800/50",
  ],
};

function renderWithRouter(ui: ReactElement, initialEntries: string[] = ["/"]) {
  return render(<MemoryRouter initialEntries={initialEntries}>{ui}</MemoryRouter>);
}

function withStatus(status: ProductStatus): CatalogProduct {
  return { ...MOCK_PRODUCTS[0], status };
}

describe("ProductCard", () => {
  test("renders the name, the category micro-pill and the primary-color dots", () => {
    const item = MOCK_PRODUCTS.find((product) => product.metadata.primaryColors?.length)!;
    renderWithRouter(<ProductCard item={item} householdId="h1" />);

    expect(screen.getByText(item.name)).toBeInTheDocument();
    expect(screen.getByText(item.category)).toBeInTheDocument();
    expect(screen.getByTestId("color-dots")).toBeInTheDocument();
    expect(screen.getByTestId("color-dots").children).toHaveLength(item.metadata.primaryColors!.length);
  });

  test("omits the color dots when the metadata carries no colors (never placeholder dots)", () => {
    const item = MOCK_PRODUCTS.find((product) => !product.metadata.primaryColors?.length)!;
    renderWithRouter(<ProductCard item={item} householdId="h1" />);

    expect(screen.queryByTestId("color-dots")).not.toBeInTheDocument();
  });

  test("uses the exact DQ3 badge class pair for every status", () => {
    for (const status of Object.keys(DQ3_PAIRS) as ProductStatus[]) {
      const { unmount } = renderWithRouter(<ProductCard item={withStatus(status)} householdId="h1" />);
      const badge = screen.getByTestId("status-badge");
      expect(badge).toHaveClass(...DQ3_PAIRS[status]);
      expect(BADGE_CLASS[status]).toBe(DQ3_PAIRS[status].join(" "));
      unmount();
    }
  });

  test("the failed card shows the rose badge, the hairline well border, and both warning icons", () => {
    renderWithRouter(<ProductCard item={withStatus("failed")} householdId="h1" />);

    expect(screen.getByTestId("status-badge")).toHaveClass("badge-failed");
    expect(screen.getByTestId("product-card-well").className).toContain("border-rose-500/30");
    expect(screen.getByTestId("failed-warning")).toBeInTheDocument();
    expect(screen.getByTestId("title-error-icon")).toBeInTheDocument();
  });

  test("the whole card links to the existing asset detail route", () => {
    const item = MOCK_PRODUCTS[0];
    renderWithRouter(<ProductCard item={item} householdId="h1" />);

    expect(screen.getByTestId("product-card")).toHaveAttribute(
      "href",
      `/assets/${item.id}?household_id=h1`
    );
  });

  test("a broken image falls back to the neutral glyph and never renders a broken icon", () => {
    const item = MOCK_PRODUCTS.find((product) => product.cutoutUrl)!;
    renderWithRouter(<ProductCard item={item} householdId="h1" />);
    const image = screen.getByRole("img");

    fireEvent.error(image);

    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    expect(screen.queryByTestId("failed-warning")).not.toBeInTheDocument();
    expect(screen.getByTestId("product-fallback-icon")).toBeInTheDocument();
  });

  test("the fallback glyph shows only for a sourceless item and vanishes when media exists", () => {
    const sourceless: CatalogProduct = {
      ...MOCK_PRODUCTS[0],
      cutoutUrl: undefined,
      sceneUrl: undefined,
      evidenceId: undefined,
    };

    const withMedia = renderWithRouter(<ProductCard item={MOCK_PRODUCTS[0]} householdId="h1" />);
    expect(screen.queryByTestId("product-fallback-icon")).not.toBeInTheDocument();
    withMedia.unmount();

    renderWithRouter(<ProductCard item={sourceless} householdId="h1" />);
    expect(screen.getByTestId("product-fallback-icon")).toBeInTheDocument();
  });

  test("cards size to their content: no fixed 3:4 dead space, the media well stays 1:1 (SG-105 G4)", () => {
    renderWithRouter(<ProductCard item={MOCK_PRODUCTS[0]} householdId="h1" />);

    expect(screen.getByTestId("product-card").style.aspectRatio).toBe("");
    expect(screen.getByTestId("product-card-well").style.aspectRatio).toBe("1 / 1");
  });
});

describe("ProductCardSkeleton", () => {
  test("is aria-hidden, keeps the 3:4 shape and pulses", () => {
    render(<ProductCardSkeleton />);
    const skeleton = screen.getByTestId("product-skeleton");

    expect(skeleton).toHaveAttribute("aria-hidden", "true");
    expect(skeleton.style.aspectRatio).toBe("3 / 4");
    expect(skeleton.querySelectorAll(".animate-pulse").length).toBe(3);
  });
});

describe("ProductGrid", () => {
  test("the grid renders one card per item inside the responsive grid region", () => {
    renderWithRouter(<ProductGrid items={MOCK_PRODUCTS} density="grid" householdId="h1" />);

    expect(screen.getByTestId("catalog-grid")).toBeInTheDocument();
    expect(screen.getAllByTestId("product-card")).toHaveLength(MOCK_PRODUCTS.length);
  });

  test("the grid stylesheet carries the 2/3/4/5 responsive breakpoints", () => {
    renderWithRouter(<ProductGrid items={MOCK_PRODUCTS} density="grid" householdId="h1" />);
    const css = screen.getByTestId("catalog-grid-style").textContent ?? "";

    expect(css).toContain("repeat(2");
    expect(css).toContain("repeat(3");
    expect(css).toContain("repeat(4");
    expect(css).toContain("repeat(5");
    expect(css).toContain("@media");
  });

  test("the compact table renders the seven DQ5 columns in order", () => {
    renderWithRouter(<ProductGrid items={MOCK_PRODUCTS} density="table" householdId="h1" />);

    const headers = screen.getAllByRole("columnheader").map((cell) => cell.textContent);
    expect(headers).toEqual([
      "Asset",
      "Name",
      "Category",
      "Status",
      "Dimensions/Specs",
      "Added",
      "Actions",
    ]);
  });

  test("a sourceless row renders the fallback glyph in the table thumb", () => {
    const sourceless: CatalogProduct = {
      ...MOCK_PRODUCTS[0],
      cutoutUrl: undefined,
      sceneUrl: undefined,
      evidenceId: undefined,
    };
    renderWithRouter(<ProductGrid items={[sourceless]} density="table" householdId="h1" />);

    expect(screen.getByTestId("product-fallback-icon")).toBeInTheDocument();
  });

  test("the compact table rides in a labelled horizontal scroll container (no page-level overflow)", () => {
    renderWithRouter(<ProductGrid items={MOCK_PRODUCTS} density="table" householdId="h1" />);

    const scroller = screen.getByTestId("table-scroll");
    expect(scroller).toHaveAttribute("role", "region");
    expect(scroller).toHaveAccessibleName("Product results table");
    expect(scroller).toHaveStyle({ overflowX: "auto" });
    expect(scroller).toContainElement(screen.getByRole("table", { name: "Product results" }));

    let node: HTMLElement | null = scroller.parentElement;
    while (node && node !== document.body) {
      expect(node.style.overflowX).not.toBe("auto");
      expect(node.style.overflowX).not.toBe("scroll");
      node = node.parentElement;
    }
  });

  test("absent specs render an honest em dash, never an invented value", () => {
    const item = MOCK_PRODUCTS.find(
      (product) => !product.metadata.dimensions && !product.metadata.material
    )!;
    renderWithRouter(<ProductGrid items={[item]} density="table" householdId="h1" />);

    expect(screen.getByText("—")).toBeInTheDocument();
  });

  test("a table row click navigates to the asset detail route", async () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route
            path="/"
            element={<ProductGrid items={[MOCK_PRODUCTS[0]]} density="table" householdId="h1" />}
          />
          <Route path="/assets/:id" element={<div>detail probe</div>} />
        </Routes>
      </MemoryRouter>
    );

    fireEvent.click(screen.getByTestId("product-row"));
    expect(await screen.findByText("detail probe")).toBeInTheDocument();
  });

  test("the ghost actions button opens the detail route and no delete control ships", async () => {
    const item = MOCK_PRODUCTS[0];
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<ProductGrid items={[item]} density="table" householdId="h1" />} />
          <Route path="/assets/:id" element={<div>detail probe</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.queryByRole("button", { name: /delete/i })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: `Actions for ${item.name}` }));
    expect(await screen.findByText("detail probe")).toBeInTheDocument();
  });

  test("an empty result shows the dashed canvas whose Import New Item CTA opens the import dialog", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<ProductGrid items={[]} density="grid" householdId="h1" />} />
          <Route path="/capture" element={<div>capture probe</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByTestId("catalog-grid-empty")).toBeInTheDocument();
    fireEvent.click(screen.getByText(/import new item/i));

    expect(screen.getByRole("dialog", { name: "Import assets" })).toBeInTheDocument();
    expect(screen.queryByText("capture probe")).not.toBeInTheDocument();
  });

  test("loading shows skeleton cards equal to the page limit and marks the region busy", () => {
    renderWithRouter(<ProductGrid items={[]} density="grid" householdId="h1" loading limit={20} />);

    expect(screen.getByRole("region", { name: /product results/i })).toHaveAttribute(
      "aria-busy",
      "true"
    );
    expect(screen.getAllByTestId("product-skeleton")).toHaveLength(20);
  });

  test("formatRelativeDate reads the live clock through an injectable now", () => {
    const now = Date.parse("2026-09-16T12:00:00Z");
    expect(formatRelativeDate("2026-09-16T11:59:30Z", now)).toBe("just now");
    expect(formatRelativeDate("2026-09-16T11:30:00Z", now)).toBe("30m ago");
    expect(formatRelativeDate("2026-09-16T06:00:00Z", now)).toBe("6h ago");
    expect(formatRelativeDate("2026-09-10T12:00:00Z", now)).toBe("6d ago");
    expect(formatRelativeDate("not-a-date", now)).toBe("—");
  });
});

describe("mockProducts", () => {
  test("spans at least four DQ1 categories and all four statuses via the real mapper", () => {
    const categories = new Set(MOCK_PRODUCTS.map((product) => product.category));
    const statuses = new Set(MOCK_PRODUCTS.map((product) => product.status));

    expect(categories.size).toBeGreaterThanOrEqual(4);
    expect(statuses).toEqual(new Set<ProductStatus>(["raw", "processed", "rendered", "failed"]));
    expect(MOCK_PRODUCTS).toHaveLength(8);
  });

  test("mock media is inline SVG data-URIs only (no network, no binaries)", () => {
    const media = MOCK_PRODUCTS.flatMap((product) => [product.cutoutUrl, product.sceneUrl]).filter(
      (url): url is string => Boolean(url)
    );

    expect(media.length).toBeGreaterThan(0);
    for (const url of media) {
      expect(url.startsWith("data:image/svg+xml")).toBe(true);
    }
  });

  test("the mapper output carries no rawResponse key", () => {
    function hasRawResponseKey(value: unknown): boolean {
      if (value === null || typeof value !== "object") return false;
      if (Object.prototype.hasOwnProperty.call(value, "rawResponse")) return true;
      return Object.values(value as Record<string, unknown>).some(hasRawResponseKey);
    }

    for (const product of MOCK_PRODUCTS) {
      expect(hasRawResponseKey(product)).toBe(false);
    }
  });
});

describe("ProductCard onSelect", () => {
  const item = MOCK_PRODUCTS[0];

  test("with onSelect, a click selects the asset id and does not navigate", () => {
    const onSelect = vi.fn();
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route
            path="/"
            element={<ProductCard item={item} householdId="h1" onSelect={onSelect} />}
          />
          <Route path="/assets/:id" element={<div>detail probe</div>} />
        </Routes>
      </MemoryRouter>
    );

    fireEvent.click(screen.getByTestId("product-card"));

    expect(onSelect).toHaveBeenCalledTimes(1);
    expect(onSelect).toHaveBeenCalledWith(item.id);
    expect(screen.queryByText("detail probe")).not.toBeInTheDocument();
  });

  test("with onSelect, Enter and Space select the asset id without navigating", () => {
    const onSelect = vi.fn();
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route
            path="/"
            element={<ProductCard item={item} householdId="h1" onSelect={onSelect} />}
          />
          <Route path="/assets/:id" element={<div>detail probe</div>} />
        </Routes>
      </MemoryRouter>
    );

    const card = screen.getByTestId("product-card");
    fireEvent.keyDown(card, { key: "Enter" });
    fireEvent.keyDown(card, { key: " " });

    expect(onSelect).toHaveBeenNthCalledWith(1, item.id);
    expect(onSelect).toHaveBeenNthCalledWith(2, item.id);
    expect(screen.queryByText("detail probe")).not.toBeInTheDocument();
  });

  test("without onSelect, a click still navigates to the detail route", async () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<ProductCard item={item} householdId="h1" />} />
          <Route path="/assets/:id" element={<div>detail probe</div>} />
        </Routes>
      </MemoryRouter>
    );

    fireEvent.click(screen.getByTestId("product-card"));

    expect(await screen.findByText("detail probe")).toBeInTheDocument();
  });
});

describe("ProductGrid onSelect", () => {
  const item = MOCK_PRODUCTS[0];

  function renderGrid(density: "grid" | "table", onSelect: (id: string) => void) {
    return render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route
            path="/"
            element={
              <ProductGrid items={[item]} density={density} householdId="h1" onSelect={onSelect} />
            }
          />
          <Route path="/assets/:id" element={<div>detail probe</div>} />
        </Routes>
      </MemoryRouter>
    );
  }

  test("a table row click with onSelect selects instead of navigating", () => {
    const onSelect = vi.fn();
    renderGrid("table", onSelect);

    fireEvent.click(screen.getByTestId("product-row"));

    expect(onSelect).toHaveBeenCalledWith(item.id);
    expect(screen.queryByText("detail probe")).not.toBeInTheDocument();
  });

  test("Enter on a table row with onSelect selects instead of navigating", () => {
    const onSelect = vi.fn();
    renderGrid("table", onSelect);

    fireEvent.keyDown(screen.getByTestId("product-row"), { key: "Enter" });

    expect(onSelect).toHaveBeenCalledWith(item.id);
    expect(screen.queryByText("detail probe")).not.toBeInTheDocument();
  });

  test("the ... actions button with onSelect selects instead of navigating", () => {
    const onSelect = vi.fn();
    renderGrid("table", onSelect);

    fireEvent.click(screen.getByRole("button", { name: `Actions for ${item.name}` }));

    expect(onSelect).toHaveBeenCalledWith(item.id);
    expect(screen.queryByText("detail probe")).not.toBeInTheDocument();
  });

  test("the grid density passes onSelect through to the cards", () => {
    const onSelect = vi.fn();
    renderGrid("grid", onSelect);

    fireEvent.click(screen.getByTestId("product-card"));

    expect(onSelect).toHaveBeenCalledWith(item.id);
    expect(screen.queryByText("detail probe")).not.toBeInTheDocument();
  });
});

describe("CatalogPage drawer wiring", () => {
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

  function renderCatalog(client: QueryClient) {
    return render(
      <QueryClientProvider client={client}>
        <ThemeProvider>
          <MemoryRouter initialEntries={["/"]}>
            <CatalogPage />
          </MemoryRouter>
        </ThemeProvider>
      </QueryClientProvider>
    );
  }

  beforeEach(() => {
    window.localStorage.clear();
    api.apiGet.mockReset();
    api.apiPatch.mockReset();
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
      if (path === "/v1/assets/a-drill") {
        return Promise.resolve(catalogAsset);
      }
      return Promise.resolve(null);
    });
  });

  test("a catalog card click opens the drawer for that asset and close clears it", async () => {
    renderCatalog(new QueryClient({ defaultOptions: { queries: { retry: false } } }));

    fireEvent.click(await screen.findByTestId("product-card"));

    expect(await screen.findByTestId("inspector-drawer")).toBeInTheDocument();
    expect(screen.getByTestId("drawer-title")).toHaveTextContent("Drill");

    fireEvent.click(screen.getByRole("button", { name: "Close inspector" }));

    await waitFor(() =>
      expect(screen.queryByTestId("inspector-drawer")).not.toBeInTheDocument()
    );
  });

  test("a save from the mounted drawer invalidates the assets + asset query keys", async () => {
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const spy = vi.spyOn(client, "invalidateQueries");
    api.apiPatch.mockResolvedValue({ ...catalogAsset, display_name: "Renamed" });
    renderCatalog(client);

    fireEvent.click(await screen.findByTestId("product-card"));
    await screen.findByTestId("inspector-drawer");

    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Renamed" } });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));

    await waitFor(() => expect(spy).toHaveBeenCalledWith({ queryKey: ["assets"] }));
    expect(spy).toHaveBeenCalledWith({ queryKey: ["asset", "a-drill"] });
  });

  test("an asset with evidence_ids renders its evidence thumbnail (the badge is reachable)", async () => {
    const withEvidence: Asset = { ...catalogAsset, evidence_ids: ["ev-thumb-1"] };
    api.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/households") {
        return Promise.resolve([{ id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" }]);
      }
      if (path === "/v1/assets/facets") {
        return Promise.resolve({
          asset_type: { "Hardware & Tools": 1 },
          status: { ACTIVE: 1 },
          has_evidence: { with: 1, without: 0 },
        });
      }
      if (path === "/v1/assets") {
        return Promise.resolve({ items: [withEvidence], next_cursor: null });
      }
      return Promise.resolve(null);
    });

    renderCatalog(new QueryClient({ defaultOptions: { queries: { retry: false } } }));

    const image = await screen.findByRole("img");
    expect(image).toHaveAttribute(
      "src",
      expect.stringContaining("/v1/evidence/ev-thumb-1/thumb/256")
    );
  });
});
