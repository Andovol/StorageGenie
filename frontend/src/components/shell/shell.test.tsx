import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "../../App";
import { CatalogPage } from "../../routes/CatalogPage";
import { ThemeProvider } from "../../theme/ThemeProvider";
import { HouseholdProvider } from "../../hooks/HouseholdContext";
import { assetToProductItem } from "../../types/product";
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
  // SG-196: CatalogPage reads household selection from the shared context;
  // preserved behavior: every catalog assertion below is unchanged.
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
  test("orders by use-by first, then recently added and name (SG-331 T2: status gone)", () => {
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

    // SG-331 T2: past oldest first, then soonest, then no-date, ties by name.
    const dated = [
      { ...products[0], useBy: "2030-05-06" },
      { ...products[1], useBy: null },
      { ...products[2], useBy: "2026-10-27" },
      { ...products[3], useBy: "2026-11-21" },
    ];
    expect(sortCatalog(dated, "useby").map((i) => i.name)).toEqual([
      "Shirt",
      "Mystery",
      "Drill",
      "Zap",
    ]);
  });
});

describe("Catalog shell", () => {
  test("the header carries no count box; Your things names the LOADED item count (SG-330 R2+R3: Showing box -> heading)", async () => {
    renderCatalog();
    expect(await screen.findByText("Drill")).toBeInTheDocument();
    expect(screen.queryByText(/Showing:/)).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Your things" })).toBeInTheDocument();
    expect(screen.getByText("4 things")).toBeInTheDocument();
  });

  test("the toolbar renders All plus one text tab per real asset_type vocabulary, no counts (SG-331 T1: counted pill -> text tab)", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    const all = await screen.findByRole("button", { name: "All" });
    expect(all).toHaveAttribute("aria-pressed", "true");
    expect(all.style.fontSize).toBe("15px");
    for (const key of ["Hardware & Tools", "Electronics & Gadgets", "Apparel & Textiles", "Uncategorized"]) {
      expect(screen.getByRole("button", { name: key })).toBeInTheDocument();
    }
    expect(screen.queryByRole("button", { name: "All (4)" })).not.toBeInTheDocument();
  });

  test("category pills and cards share one vocabulary through the real server filter (SG-105 G4)", async () => {
    renderCatalog();
    await screen.findByText("Drill");

    // The raw facet key is `unknown`; the pill must speak the same word the
    // card's `toProductCategory` mapping shows.
    const pill = await screen.findByRole("button", { name: "Uncategorized" });
    // SG-331 T1: the tab and the card now read the same word, so scope the
    // card assertion to its kind line (was: getByText, unique when tabs
    // carried counts).
    expect(screen.getAllByTestId("product-kind").map((node) => node.textContent)).toContain("Uncategorized");

    fireEvent.click(pill);

    await waitFor(() =>
      expect(
        api.apiGet.mock.calls.some(
          ([path, params]) =>
            path === "/v1/assets" &&
            (params as Record<string, string> | undefined)?.asset_type === "unknown"
        )
      ).toBe(true)
    );
    expect(pill).toHaveAttribute("aria-pressed", "true");
  });

  test("colliding asset_type keys stay separate pills with exact server filters (SG-118 G3)", async () => {
    api.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/households") {
        return Promise.resolve([{ id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" }]);
      }
      if (path === "/v1/assets/facets") {
        // `unknown` and the literal `Uncategorized` both normalize to
        // "Uncategorized" and carry the SAME count, which is the old
        // first-key-wins / label-collision edge.
        return Promise.resolve({
          asset_type: { unknown: 2, Uncategorized: 2 },
          status: {},
          has_evidence: {},
        });
      }
      if (path === "/v1/saved-searches") {
        return Promise.resolve({ items: [] });
      }
      if (path === "/v1/assets") {
        return Promise.resolve({ items: assets, next_cursor: null });
      }
      return Promise.resolve(null);
    });

    renderCatalog();
    await screen.findByText("Drill");

    const literal = await screen.findByRole("button", { name: "Uncategorized" });
    const alias = await screen.findByRole("button", { name: "Uncategorized · unknown" });
    expect(literal).toBeInTheDocument();
    expect(alias).toBeInTheDocument();

    fireEvent.click(alias);
    await waitFor(() =>
      expect(
        api.apiGet.mock.calls.some(
          ([p, params]) =>
            p === "/v1/assets" &&
            (params as Record<string, string> | undefined)?.asset_type === "unknown"
        )
      ).toBe(true)
    );

    fireEvent.click(literal);
    await waitFor(() =>
      expect(
        api.apiGet.mock.calls.some(
          ([p, params]) =>
            p === "/v1/assets" &&
            (params as Record<string, string> | undefined)?.asset_type === "Uncategorized"
        )
      ).toBe(true)
    );
  });

  test("the catalog main rides the shared centered container (SG-105 G1)", async () => {
    renderCatalog();
    await screen.findByText("Drill");

    const main = document.querySelector("main.page-container") as HTMLElement;
    expect(main).not.toBeNull();
    expect(main).toHaveStyle({ maxWidth: "1100px", marginLeft: "auto", marginRight: "auto" });
  });

  test("a category tab filters server-side and carries the underline style when active (SG-331 T1: pill -> tab)", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    const pill = await screen.findByRole("button", { name: "Electronics & Gadgets" });
    fireEvent.click(pill);

    expect(pill).toHaveAttribute("aria-pressed", "true");
    expect(pill).toHaveClass("focus-ring");
    expect(pill.style.fontWeight).toBe("600");
    expect(pill.style.borderBottom).toContain("2px solid");
    expect(screen.getByRole("button", { name: "All" }).style.color).toBe("hsl(var(--ink-muted))");
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
    fireEvent.change(screen.getByLabelText("Search your things"), { target: { value: "shi" } });
    expect(screen.getByText("Search: shi")).toBeInTheDocument();

    await waitFor(() => expect(screen.getByText("Shirt")).toBeInTheDocument());
    await waitFor(() => expect(screen.queryByText("Zap")).not.toBeInTheDocument());
  });

  test("the sort dropdown orders the loaded set client-side", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    fireEvent.change(screen.getByLabelText("Sort"), { target: { value: "name" } });

    const cards = renderedAssetCards();
    expect(cards[0].textContent).toContain("Drill");
    expect(cards[1].textContent).toContain("Mystery");
    expect(cards[2].textContent).toContain("Shirt");
    expect(cards[3].textContent).toContain("Zap");
  });

  test("Clear all empties all three filters: query, pill and sort", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    fireEvent.change(screen.getByLabelText("Search your things"), { target: { value: "zap" } });
    fireEvent.click(await screen.findByRole("button", { name: "Electronics & Gadgets" }));
    fireEvent.change(screen.getByLabelText("Sort"), { target: { value: "name" } });
    const clearAll = screen.getByRole("button", { name: /clear all/i });
    expect(clearAll.style.color).toBe("hsl(var(--link))");
    expect(clearAll.style.textDecoration).toContain("underline");
    fireEvent.click(clearAll);

    expect(screen.getByLabelText("Search your things")).toHaveValue("");
    expect(screen.getByRole("button", { name: "All" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByLabelText("Sort")).toHaveValue("useby");
  });

  test("Cmd/Ctrl+K moves focus to the header search field", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    const input = screen.getByLabelText("Search your things");
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

  test("the header Add item CTA opens the import dialog and does not render /capture (SG-330 R2: Import Asset -> Add item)", async () => {
    render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <ThemeProvider>
          <MemoryRouter initialEntries={["/"]}>
            <Routes>
              <Route path="/" element={<HouseholdProvider><CatalogPage /></HouseholdProvider>} />
              <Route path="/capture" element={<div>capture probe</div>} />
            </Routes>
          </MemoryRouter>
        </ThemeProvider>
      </QueryClientProvider>
    );
    await screen.findByText("Drill");

    fireEvent.click(screen.getByRole("link", { name: "Add item" }));

    expect(screen.getByRole("dialog", { name: "Import assets" })).toBeInTheDocument();
    expect(screen.queryByText("capture probe")).not.toBeInTheDocument();
  });

  test("List renders the real table view (the SG-045 note is gone)", async () => {
    renderCatalog();
    await screen.findByText("Drill");
    fireEvent.click(screen.getByRole("button", { name: "List" }));

    expect(screen.getByRole("button", { name: "List" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.queryByText(/table view arrives with the new cards/i)).not.toBeInTheDocument();
    expect(screen.getByRole("table", { name: "Product results" })).toBeInTheDocument();
    expect(screen.getByText("Drill")).toBeInTheDocument();
  });

  test("the landing route renders the App nav with the Analytics link (D95)", async () => {
    renderApp(["/"]);
    await screen.findByText("Drill");

    // SG-073 D95: <Nav /> now renders unconditionally, so the landing route
    // carries the Analytics link and the legacy nav footer line. SG-105 G4:
    // the Catalog's own AppHeader no longer repeats the brand, so exactly one
    // brand row remains on the route.
    expect(await screen.findByRole("link", { name: "Analytics" })).toBeInTheDocument();
    // SG-301 G2: the "Phase 0 · local-first" nav footer is gone on purpose;
    // the Inbox link (with its badge) proves the nav rendered instead.
    expect(screen.getByRole("link", { name: /Inbox/ })).toBeInTheDocument();
    expect(screen.getAllByText("StorageGenie")).toHaveLength(1);
  });

  test("a non-catalog route keeps the shared legacy nav (now carrying Expiry)", async () => {
    renderApp(["/capture"]);

    // SG-301 G2: the "Phase 0 · local-first" nav footer is gone on purpose;
    // the Import Asset link proves the shared legacy nav rendered instead.
    expect(await screen.findByRole("link", { name: "Import Asset" })).toBeInTheDocument();
    expect(screen.getByText("Add an item")).toBeInTheDocument();
    expect(screen.getAllByText("StorageGenie")).toHaveLength(1);
    // SG-108: the /expiry route adds its nav entry; every other link is unchanged.
    expect(screen.getByRole("link", { name: "Expiry" })).toHaveAttribute("href", "/expiry");
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

    // SG-330 R2+R3: the count lives under Your things (was SG-301 G2 "Showing: N item(s)").
    expect(screen.queryByText(/Showing:/)).not.toBeInTheDocument();
    expect(screen.getByText("1 thing")).toBeInTheDocument();
    expect(screen.queryByText("1 things")).not.toBeInTheDocument();
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

    fireEvent.change(screen.getByLabelText("Search your things"), { target: { value: "shi" } });
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

    await waitFor(() => expect(screen.getByLabelText("Search your things")).toHaveValue("zap"));
    expect(screen.getByRole("button", { name: "Electronics & Gadgets" })).toHaveAttribute(
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
    expect(none.style.color).toBe("hsl(var(--ink-muted))");
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

  test("the toolbar carries NO household control; the saved-search selection has no switch to react to (SG-208/D-13)", async () => {
    mockSavedSearches([saved]);
    renderCatalog();
    await screen.findByText("Drill");

    fireEvent.change(await screen.findByLabelText("Saved searches"), { target: { value: "s1" } });
    await screen.findByText("q: zap");

    // Non-vacuity: the toolbar's own comboboxes render (sort + saved searches),
    // so the role query is proven live; no household combobox exists to reset
    // the selection, and the applied one stays.
    expect(screen.getByLabelText("Sort")).toBeInTheDocument();
    expect(screen.queryAllByRole("combobox", { name: /household/i })).toHaveLength(0);
    expect((screen.getByLabelText("Saved searches") as HTMLSelectElement).value).toBe("s1");
  });
});
