import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "../../App";
import { CatalogPage } from "../../routes/CatalogPage";
import { ThemeProvider } from "../../theme/ThemeProvider";
import { assetToProductItem, type ProductStatus } from "../../types/product";
import { sortCatalog } from "./CatalogToolbar";
import type { Asset } from "../../api/types";

const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  buildUrl: (path: string) => path,
}));
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

function renderApp(initialEntries: string[]) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ThemeProvider>
        <MemoryRouter initialEntries={initialEntries}>
          <App />
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
  api.apiPost.mockReset();
  api.apiPost.mockResolvedValue(undefined);
  const facets = {
    asset_type: {
      "Hardware & Tools": 1,
      "Electronics & Gadgets": 1,
      "Apparel & Textiles": 1,
      unknown: 1,
    },
    status: { ACTIVE: 1, DRAFT: 1, PENDING_REVIEW: 1, ARCHIVED: 1 },
    has_evidence: { with: 0, without: 4 },
  };
  api.apiGet.mockImplementation((path: string, params?: Record<string, string>) => {
    if (path === "/v1/households") {
      return Promise.resolve([{ id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" }]);
    }
    if (path === "/v1/assets/facets") {
      return Promise.resolve(facets);
    }
    if (path === "/v1/saved-searches") {
      return Promise.resolve({ items: [] });
    }
    if (path === "/v1/assets") {
      let items = assets;
      if (params?.asset_type) {
        items = items.filter((asset) => asset.asset_type === params.asset_type);
      }
      if (params?.q) {
        const needle = params.q.toLowerCase();
        items = items.filter((asset) => (asset.display_name ?? "").toLowerCase().includes(needle));
      }
      return Promise.resolve({ items, next_cursor: null });
    }
    return Promise.resolve(null);
  });
});

afterEach(() => {
  vi.clearAllMocks();
  vi.unstubAllGlobals();
});

describe("sortCatalog (real mapper data)", () => {
  // Filtering (query + category) moved to the server (SG-064 G2); the client
  // path only orders the loaded page now.
  test("orders by recently added, name, and processing status", () => {
    expect(sortCatalog(products, "recent").map((i) => i.name)).toEqual([
      "Mystery",
      "Zap",
      "Shirt",
      "Drill",
    ]);
    expect(sortCatalog(products, "name").map((i) => i.name)).toEqual([
      "Drill",
      "Mystery",
      "Shirt",
      "Zap",
    ]);

    const statuses: ProductStatus[] = ["processed", "raw", "rendered", "raw"];
    const statusItems = products.map((item, index) => ({ ...item, status: statuses[index] }));
    expect(sortCatalog(statusItems, "status").map((i) => i.status)).toEqual([
      "processed",
      "raw",
      "raw",
      "rendered",
    ]);
  });
});

describe("Catalog shell", () => {
  test("the header labels the LOADED item count, not a household total", async () => {
    renderCatalog();
    expect(await screen.findByText("Drill")).toBeInTheDocument();
    expect(screen.getByLabelText(/total loaded items: 4/i)).toHaveTextContent("Total: 4 items");
  });

  test("the toolbar renders All plus one counted pill per real asset_type", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    const all = await screen.findByRole("button", { name: "All (4)" });
    expect(all).toHaveAttribute("aria-pressed", "true");
    const counts: Record<string, number> = {
      "Hardware & Tools": 1,
      "Electronics & Gadgets": 1,
      "Apparel & Textiles": 1,
      unknown: 1,
    };
    for (const [key, count] of Object.entries(counts)) {
      expect(screen.getByRole("button", { name: `${key} (${count})` })).toBeInTheDocument();
    }
  });

  test("a category pill filters server-side and carries the primary style when active", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    const pill = await screen.findByRole("button", { name: "Electronics & Gadgets (1)" });
    fireEvent.click(pill);

    expect(pill).toHaveAttribute("aria-pressed", "true");
    expect(pill).toHaveClass("bg-primary");
    await waitFor(() => expect(screen.getByText("Zap")).toBeInTheDocument());
    expect(screen.queryByText("Drill")).not.toBeInTheDocument();
    const listCall = api.apiGet.mock.calls.find(
      ([path, params]) =>
        path === "/v1/assets" &&
        (params as Record<string, string> | undefined)?.asset_type === "Electronics & Gadgets"
    );
    expect(listCall).toBeTruthy();
  });

  test("typing in the header search narrows via the server-side query", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    fireEvent.change(screen.getByLabelText("Search catalog"), { target: { value: "shi" } });
    expect(screen.getByText("Search: shi")).toBeInTheDocument();

    await waitFor(() => expect(screen.getByText("Shirt")).toBeInTheDocument());
    await waitFor(() => expect(screen.queryByText("Zap")).not.toBeInTheDocument());
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
    fireEvent.click(await screen.findByRole("button", { name: "Electronics & Gadgets (1)" }));
    fireEvent.change(screen.getByLabelText("Sort catalog"), { target: { value: "name" } });
    fireEvent.click(screen.getByRole("button", { name: /clear all/i }));

    expect(screen.getByLabelText("Search catalog")).toHaveValue("");
    expect(screen.getByRole("button", { name: "All (4)" })).toHaveAttribute("aria-pressed", "true");
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

  test("the header Import Asset CTA opens the import dialog and does not render /capture", async () => {
    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <ThemeProvider>
          <MemoryRouter initialEntries={["/"]}>
            <Routes>
              <Route path="/" element={<CatalogPage />} />
              <Route path="/capture" element={<div>capture probe</div>} />
            </Routes>
          </MemoryRouter>
        </ThemeProvider>
      </QueryClientProvider>
    );
    await screen.findByText("Drill");

    fireEvent.click(screen.getByRole("link", { name: /import asset/i }));

    expect(screen.getByRole("dialog", { name: "Import assets" })).toBeInTheDocument();
    expect(screen.queryByText("capture probe")).not.toBeInTheDocument();
  });

  test("Compact Table renders the real table view (the SG-045 note is gone)", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    fireEvent.click(screen.getByRole("button", { name: "Compact Table" }));

    expect(screen.getByRole("button", { name: "Compact Table" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.queryByText(/table view arrives with the new cards/i)).not.toBeInTheDocument();
    expect(screen.getByRole("table", { name: "Product results" })).toBeInTheDocument();
    expect(screen.getByText("Drill")).toBeInTheDocument();
  });

  test("the catalog route renders ONE StorageGenie wordmark (legacy nav gone)", async () => {
    renderApp(["/"]);
    await screen.findByText("Drill");

    expect(screen.getAllByText("StorageGenie")).toHaveLength(1);
    expect(screen.queryByText("Phase 0 · local-first")).not.toBeInTheDocument();
  });

  test("a non-catalog route keeps the byte-identical legacy nav", async () => {
    renderApp(["/capture"]);

    expect(await screen.findByText("Phase 0 · local-first")).toBeInTheDocument();
    expect(screen.getByText("Capture — Manual Create")).toBeInTheDocument();
    expect(screen.getAllByText("StorageGenie")).toHaveLength(1);
  });

  test("the header count uses the singular only for one loaded item", async () => {
    api.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/households") {
        return Promise.resolve([{ id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" }]);
      }
      if (path === "/v1/assets") {
        return Promise.resolve({ items: [assets[0]], next_cursor: null });
      }
      return Promise.resolve(null);
    });

    renderCatalog();
    await screen.findByText("Drill");

    expect(screen.getByText("Total: 1 item")).toBeInTheDocument();
    expect(screen.queryByText("Total: 1 items")).not.toBeInTheDocument();
  });
});

describe("Saved searches (SG-068)", () => {
  const saved = {
    id: "s1",
    household_id: "h1",
    name: "Electronics",
    query: { q: "zap", asset_type: "Electronics & Gadgets" },
    created_at: "2026-09-17T00:00:00Z",
  };

  function mockSavedSearches(items: unknown[]) {
    api.apiGet.mockImplementation((path: string, params?: Record<string, string>) => {
      if (path === "/v1/households") {
        return Promise.resolve([
          { id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" },
          { id: "h2", name: "Cabin", created_at: "2026-09-01T00:00:00Z" },
        ]);
      }
      if (path === "/v1/saved-searches") {
        return Promise.resolve({ items });
      }
      if (path === "/v1/assets/facets") {
        return Promise.resolve({
          asset_type: {
            "Hardware & Tools": 1,
            "Electronics & Gadgets": 1,
            "Apparel & Textiles": 1,
            unknown: 1,
          },
          status: { ACTIVE: 1, DRAFT: 1, PENDING_REVIEW: 1, ARCHIVED: 1 },
          has_evidence: { with: 0, without: 4 },
        });
      }
      if (path === "/v1/assets") {
        let listed = assets;
        if (params?.asset_type) {
          listed = listed.filter((asset) => asset.asset_type === params.asset_type);
        }
        if (params?.q) {
          const needle = params.q.toLowerCase();
          listed = listed.filter((asset) =>
            (asset.display_name ?? "").toLowerCase().includes(needle)
          );
        }
        return Promise.resolve({ items: listed, next_cursor: null });
      }
      return Promise.resolve(null);
    });
  }

  test("Save search stays disabled until a filter is active, then POSTs the filter set", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    const saveButton = screen.getByRole("button", { name: "Save search" });
    expect(saveButton).toBeDisabled();

    fireEvent.change(screen.getByLabelText("Search catalog"), { target: { value: "shi" } });
    await waitFor(() => expect(saveButton).not.toBeDisabled());

    const promptSpy = vi.spyOn(window, "prompt").mockReturnValue("Shirt searches");
    fireEvent.click(saveButton);

    await waitFor(() =>
      expect(api.apiPost).toHaveBeenCalledWith(
        "/v1/saved-searches",
        { name: "Shirt searches", query: { q: "shi" } },
        { household_id: "h1" }
      )
    );
    promptSpy.mockRestore();
  });

  test("the dropdown lists saved searches and applying one sets the same state and query", async () => {
    mockSavedSearches([saved]);
    renderCatalog();
    await screen.findByText("Drill");

    const select = await screen.findByLabelText("Saved searches");
    expect(screen.getByText("Electronics")).toBeInTheDocument();
    fireEvent.change(select, { target: { value: "s1" } });

    await waitFor(() => expect(screen.getByLabelText("Search catalog")).toHaveValue("zap"));
    expect(screen.getByRole("button", { name: "Electronics & Gadgets (1)" })).toHaveAttribute(
      "aria-pressed",
      "true"
    );
    await waitFor(() =>
      expect(
        api.apiGet.mock.calls.some(
          ([path, params]) =>
            path === "/v1/assets" &&
            (params as Record<string, string>).q === "zap" &&
            (params as Record<string, string>).asset_type === "Electronics & Gadgets"
        )
      ).toBe(true)
    );
    expect(screen.getByText("q: zap")).toBeInTheDocument();
  });

  test("a saved name round-trips and renders as TEXT, never as markup", async () => {
    mockSavedSearches([{ ...saved, name: "O'Brien <derp>" }]);
    renderCatalog();
    await screen.findByText("Drill");

    expect(await screen.findByText("O'Brien <derp>")).toBeInTheDocument();
    expect(document.querySelector("derp")).toBeNull();
  });

  test("an empty saved-search list renders a muted None yet, not an error", async () => {
    renderCatalog();
    await screen.findByText("Drill");

    const none = await screen.findByText("None yet");
    expect(none).toHaveClass("text-muted-foreground");
  });

  test("deleting from the dropdown DELETEs the saved search's id", async () => {
    mockSavedSearches([saved]);
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: "deleted", id: "s1" }),
    });
    vi.stubGlobal("fetch", fetchMock);
    renderCatalog();
    await screen.findByText("Drill");

    fireEvent.change(await screen.findByLabelText("Saved searches"), { target: { value: "s1" } });
    await screen.findByText("q: zap");
    fireEvent.click(screen.getByRole("button", { name: "Delete saved search" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toContain("/v1/saved-searches/s1");
    expect(options).toEqual({ method: "DELETE" });
  });

  test("switching household clears the applied saved-search selection", async () => {
    mockSavedSearches([saved]);
    renderCatalog();
    await screen.findByText("Drill");

    fireEvent.change(await screen.findByLabelText("Saved searches"), { target: { value: "s1" } });
    await screen.findByText("q: zap");

    fireEvent.change(screen.getByLabelText("Household"), { target: { value: "h2" } });
    await waitFor(() =>
      expect((screen.getByLabelText("Saved searches") as HTMLSelectElement).value).toBe("")
    );
  });
});
