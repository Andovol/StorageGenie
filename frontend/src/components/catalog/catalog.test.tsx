import { describe, expect, test } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import type { ReactElement } from "react";
import type { ProductStatus } from "../../types/product";
import { BADGE_CLASS, ProductCard, type CatalogProduct } from "./ProductCard";
import { ProductCardSkeleton } from "./ProductCardSkeleton";
import { ProductGrid, formatRelativeDate } from "./ProductGrid";
import { MOCK_PRODUCTS } from "./mockProducts";

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

  test("a broken image falls back to the empty well and never renders a broken icon", () => {
    const item = MOCK_PRODUCTS.find((product) => product.cutoutUrl)!;
    renderWithRouter(<ProductCard item={item} householdId="h1" />);
    const image = screen.getByRole("img");

    fireEvent.error(image);

    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    expect(screen.queryByTestId("failed-warning")).not.toBeInTheDocument();
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

  test("an empty result shows the dashed canvas with the Import New Item CTA to /capture", () => {
    renderWithRouter(<ProductGrid items={[]} density="grid" householdId="h1" />);

    expect(screen.getByText(/import new item/i)).toHaveAttribute("href", "/capture");
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
