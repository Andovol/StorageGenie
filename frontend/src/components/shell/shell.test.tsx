import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { CatalogPage } from "../../routes/CatalogPage";
import { ThemeProvider } from "../../theme/ThemeProvider";
import {
  CANONICAL_CATEGORIES,
  assetToProductItem,
  type ProductStatus,
} from "../../types/product";
import { CATEGORY_PILLS, filterAndSortCatalog } from "./CatalogToolbar";
import type { Asset } from "../../api/types";

const api = vi.hoisted(() => ({ apiGet: vi.fn() }));
vi.mock("../../api/client", () => api);

const assets: Asset[] = [
  {
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
  },
  {
    id: "a-zap",
    household_id: "h1",
    display_name: "Zap",
    asset_type: "Electronics & Gadgets",
    status: "DRAFT",
    quantity: null,
    unit: null,
    condition: null,
    version: 1,
    created_at: "2026-09-12T00:00:00Z",
    updated_at: null,
  },
  {
    id: "a-shirt",
    household_id: "h1",
    display_name: "Shirt",
    asset_type: "Apparel & Textiles",
    status: "PENDING_REVIEW",
    quantity: null,
    unit: null,
    condition: null,
    version: 1,
    created_at: "2026-09-11T00:00:00Z",
    updated_at: null,
  },
  {
    id: "a-mystery",
    household_id: "h1",
    display_name: "Mystery",
    asset_type: "unknown",
    status: "ARCHIVED",
    quantity: null,
    unit: null,
    condition: null,
    version: 1,
    created_at: "2026-09-13T00:00:00Z",
    updated_at: null,
  },
];

const products = assets.map(assetToProductItem);

function mockMatchMedia() {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    configurable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }),
  });
}

function renderCatalog() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ThemeProvider>
        <MemoryRouter initialEntries={["/"]}>
          <CatalogPage />
        </MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

function renderedAssetCards(): HTMLElement[] {
  return screen
    .getAllByRole("link")
    .filter((element) => (element.getAttribute("href") ?? "").startsWith("/assets/"));
}

beforeEach(() => {
  window.localStorage.clear();
  document.documentElement.className = "";
  mockMatchMedia();
  api.apiGet.mockReset();
  api.apiGet.mockImplementation((path: string) => {
    if (path === "/v1/households") {
      return Promise.resolve([{ id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" }]);
    }
    if (path === "/v1/assets") {
      return Promise.resolve({ items: assets, next_cursor: null });
    }
    return Promise.resolve(null);
  });
});

afterEach(() => {
  vi.clearAllMocks();
});

describe("filterAndSortCatalog (real mapper data)", () => {
  test("filters the loaded set by category pill and by the query text", () => {
    expect(
      filterAndSortCatalog(products, { q: "", category: "Electronics & Gadgets", sort: "recent" }).map((i) => i.name)
    ).toEqual(["Zap"]);
    expect(
      filterAndSortCatalog(products, { q: "shi", category: "All", sort: "recent" }).map((i) => i.name)
    ).toEqual(["Shirt"]);
    expect(
      filterAndSortCatalog(products, { q: "", category: "Uncategorized", sort: "recent" }).map((i) => i.name)
    ).toEqual(["Mystery"]);
  });

  test("orders by recently added, name, and processing status", () => {
    expect(
      filterAndSortCatalog(products, { q: "", category: "All", sort: "recent" }).map((i) => i.name)
    ).toEqual(["Mystery", "Zap", "Shirt", "Drill"]);
    expect(
      filterAndSortCatalog(products, { q: "", category: "All", sort: "name" }).map((i) => i.name)
    ).toEqual(["Drill", "Mystery", "Shirt", "Zap"]);

    const statuses: ProductStatus[] = ["processed", "raw", "rendered", "raw"];
    const statusItems = products.map((item, index) => ({ ...item, status: statuses[index] }));
    expect(
      filterAndSortCatalog(statusItems, { q: "", category: "All", sort: "status" }).map((i) => i.status)
    ).toEqual(["processed", "raw", "raw", "rendered"]);
  });
});

describe("Catalog shell", () => {
  test("the header labels the LOADED item count, not a household total", async () => {
    renderCatalog();
    expect(await screen.findByText("Drill")).toBeInTheDocument();
    expect(screen.getByLabelText(/total loaded items: 4/i)).toHaveTextContent("Total: 4 items");
  });

  test("the toolbar renders All plus the DQ1 six, with All active by default", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    expect(CATEGORY_PILLS).toEqual(["All", ...CANONICAL_CATEGORIES]);
    for (const category of CANONICAL_CATEGORIES) {
      expect(screen.getByRole("button", { name: category })).toBeInTheDocument();
    }
    expect(screen.getByRole("button", { name: "All" })).toHaveAttribute("aria-pressed", "true");
  });

  test("a category pill filters the loaded set and carries the primary style when active", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    fireEvent.click(screen.getByRole("button", { name: "Electronics & Gadgets" }));

    const pill = screen.getByRole("button", { name: "Electronics & Gadgets" });
    expect(pill).toHaveAttribute("aria-pressed", "true");
    expect(pill).toHaveClass("bg-primary");
    expect(screen.getByText("Zap")).toBeInTheDocument();
    expect(screen.queryByText("Drill")).not.toBeInTheDocument();
  });

  test("typing in the header search narrows the loaded set", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    fireEvent.change(screen.getByLabelText("Search catalog"), { target: { value: "shi" } });

    expect(screen.getByText("Shirt")).toBeInTheDocument();
    expect(screen.queryByText("Zap")).not.toBeInTheDocument();
    expect(screen.getByText("Search: shi")).toBeInTheDocument();
  });

  test("the sort dropdown orders the loaded set client-side", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    fireEvent.change(screen.getByLabelText("Sort catalog"), { target: { value: "name" } });

    const cards = renderedAssetCards();
    expect(cards[0].textContent).toContain("Drill");
    expect(cards[1].textContent).toContain("Mystery");
    expect(cards[2].textContent).toContain("Shirt");
    expect(cards[3].textContent).toContain("Zap");
  });

  test("Clear all empties all three filters: query, pill and sort", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    fireEvent.change(screen.getByLabelText("Search catalog"), { target: { value: "zap" } });
    fireEvent.click(screen.getByRole("button", { name: "Electronics & Gadgets" }));
    fireEvent.change(screen.getByLabelText("Sort catalog"), { target: { value: "name" } });
    fireEvent.click(screen.getByRole("button", { name: /clear all/i }));

    expect(screen.getByLabelText("Search catalog")).toHaveValue("");
    expect(screen.getByRole("button", { name: "All" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByLabelText("Sort catalog")).toHaveValue("recent");
  });

  test("Cmd/Ctrl+K moves focus to the header search field", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    const input = screen.getByLabelText("Search catalog");
    (input as HTMLInputElement).blur();
    expect(document.activeElement).not.toBe(input);

    fireEvent.keyDown(document, { key: "k", metaKey: true });
    expect(document.activeElement).toBe(input);

    (input as HTMLInputElement).blur();
    fireEvent.keyDown(document, { key: "k", ctrlKey: true });
    expect(document.activeElement).toBe(input);
  });

  test("the theme toggle flips the dark class on <html>", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    fireEvent.click(screen.getByRole("button", { name: /switch to dark theme/i }));
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  test("Import Asset routes to /capture", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    expect(screen.getByRole("link", { name: /import asset/i })).toHaveAttribute("href", "/capture");
  });

  test("Compact Table is present but honestly keeps the grid until the new cards land", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    fireEvent.click(screen.getByRole("button", { name: "Compact Table" }));

    expect(screen.getByRole("button", { name: "Compact Table" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText(/table view arrives with the new cards/i)).toBeInTheDocument();
    expect(screen.getByText("Drill")).toBeInTheDocument();
  });
});
