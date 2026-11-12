// SG-307r1: the three small fixes SG-307 left behind — Pantry buttons paper at
// the source with no !important band-aid, taxonomy category words in
// labelAssetType, and the system Version off the item panel.
import { afterEach, describe, expect, test, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
// @ts-expect-error: node:fs is available in the vitest runtime; @types/node is intentionally not a project dependency
import { readFileSync } from "node:fs";
import { ThemeProvider } from "../theme/ThemeProvider";
import { PantryPage } from "./PantryPage";
import { ExpiryPage } from "./ExpiryPage";
import { ItemInspectorDrawer } from "../components/shell/ItemInspectorDrawer";
import { labelAssetType } from "../lib/labels";
import type { Asset } from "../api/types";

const tokensCss = readFileSync("src/theme/tokens.css", "utf8");

const client = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPatch: vi.fn(),
  decrementQuantity: vi.fn(),
  incrementQuantity: vi.fn(),
  markGone: vi.fn(),
  putBack: vi.fn(),
  fetchExpiryStatus: vi.fn(),
  fetchAnalyticsSummary: vi.fn(),
  fetchReminders: vi.fn(),
  dismissReminder: vi.fn(),
  markReminderRead: vi.fn(),
  fetchOpenedCountdown: vi.fn(),
  clearOpenedDate: vi.fn(),
  recordOpenedDate: vi.fn(),
}));

vi.mock("../api/client", () => client);

vi.mock("../hooks/HouseholdContext", () => ({
  useHouseholdContext: () => ({
    households: [{ id: "hh", name: "Home", created_at: "2026-01-01" }],
    isError: false,
    error: null,
    householdId: "hh",
  }),
}));

function providers(children: React.ReactNode) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ThemeProvider>
        <MemoryRouter>{children}</MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

function food(id: string, name: string) {
  return {
    id,
    household_id: "hh",
    display_name: name,
    asset_type: "product",
    status: "ACTIVE",
    quantity: 2,
    unit: "pcs",
    condition: null,
    version: 1,
    created_at: "2026-09-14T00:00:00+00:00",
    evidence_ids: [],
  };
}

const taxonomy = {
  plugins: [
    {
      plugin_id: "expiry-tracker",
      version: "1.0.0",
      categories: [
        { id: "food_beverages", name: "Food & beverages", active: true, notification: "tiered-30-7-1", opened_date_tracking: false, chat: "category" },
        { id: "medicine_pharma", name: "Medicine/pharma", active: true, notification: "tiered-short", opened_date_tracking: false, chat: "category" },
        { id: "cosmetics_personal_care", name: "Cosmetics/personal care", active: true, notification: "tiered-90-30-7", opened_date_tracking: false, chat: "none" },
        { id: "household_chemicals", name: "Household chemicals", active: true, notification: "basic-expiry", opened_date_tracking: false, chat: "fallback" },
        { id: "documents_other", name: "Documents/other", active: true, notification: "long-lead-60-30", opened_date_tracking: false, chat: "fallback" },
        { id: "non_perishable", name: "Non-perishable", active: true, notification: "none", opened_date_tracking: false, chat: "none" },
      ],
      date_types: ["expiry_date", "use_by"],
      units: ["count"],
    },
  ],
};

afterEach(() => {
  vi.clearAllMocks();
});

describe("SG-307r1 fix 1: Pantry tile buttons paper at the source", () => {
  test("no tile button inline style names --card; buttons stay >= 40px tall", async () => {
    client.apiGet.mockResolvedValue({ items: [food("a", "Milk")], next_cursor: null });
    client.fetchExpiryStatus.mockResolvedValue({
      household_id: "hh",
      as_of: "2026-11-10",
      category: "food_beverages",
      rows: [
        { asset_id: "a", display_name: "Milk", category: "food_beverages", expiry_date: "2026-11-13", date_type: "expiry_date", days_remaining: 3, tier: null, bucket: "this-week" },
      ],
      summary: { by_tier: {}, by_bucket: {}, unresolved: 0, total: 1 },
      unresolved_rows: [],
    });
    client.fetchAnalyticsSummary.mockResolvedValue({ categories: { uncategorized: 0 } });
    const { container } = providers(<PantryPage />);
    const grid = await screen.findByTestId("pantry-grid");
    const tiles = within(grid).getAllByTestId("pantry-tile");
    expect(tiles.length).toBeGreaterThan(0);
    for (const tile of tiles) {
      for (const button of tile.querySelectorAll("button")) {
        expect(button.getAttribute("style") ?? "").not.toContain("--card");
      }
    }
    const useItUp = within(grid).getByRole("button", { name: "Use it up" });
    expect(useItUp.style.backgroundColor).toContain("paper");
    expect(useItUp.style.minHeight).toBe("40px");
    expect(container.querySelector("style")?.textContent ?? "").toContain("pantry-grid");
  });

  test("tokens.css has no pantry-tile rule and no !important for it", () => {
    expect(tokensCss).not.toContain("pantry-tile");
    const pantryBlocks = tokensCss.split("}").filter((block) => block.includes("pantry-tile") || block.includes("pantry-notice"));
    expect(pantryBlocks).toEqual([]);
  });
});

describe("SG-307r1 fix 2: labelAssetType speaks the taxonomy's words", () => {
  test("food_beverages reads as the Expiry page shows it, for every taxonomy key", async () => {
    client.apiGet.mockImplementation((path: string) =>
      path.includes("/v1/taxonomy") ? Promise.resolve(taxonomy) : Promise.resolve({ items: [], next_cursor: null, total: 0 })
    );
    client.fetchExpiryStatus.mockResolvedValue({
      household_id: "hh",
      as_of: "2026-09-24",
      category: null,
      rows: [
        { asset_id: "a1", display_name: "Milk", category: "food_beverages", expiry_date: "2026-09-20", date_type: "use_by", days_remaining: -4, tier: null, bucket: "expired" },
      ],
      summary: { by_tier: {}, by_bucket: { expired: 1 }, unresolved: 0, total: 1 },
      unresolved_rows: [],
    });
    client.fetchAnalyticsSummary.mockResolvedValue({
      household_id: "hh",
      as_of_date: "2026-09-24",
      generated_at: "2026-09-24T00:00:00+00:00",
      assets: { total: 1, active: 1, by_status: {} },
      categories: { taxonomy: [], counts: {}, uncategorized: 0 },
      expiry: {},
      waste: { expired_untouched: 0 },
      adherence: { suggestions: {}, review_tasks: {} },
      stats: [],
    });
    client.fetchReminders.mockResolvedValue({ household_id: "hh", unread_count: 0, items: [] });
    client.fetchOpenedCountdown.mockResolvedValue({ household_id: "hh", as_of: "2026-09-24", rows: [] });
    providers(<ExpiryPage />);
    // The Expiry page's own word for this category, from the served taxonomy
    // (the Shelf life filter option and the row's category name both show it).
    const expiryWords = await screen.findAllByText("Food & beverages");
    expect(expiryWords.length).toBeGreaterThan(0);
    expect(labelAssetType("food_beverages")).toBe("Food & beverages");
    expect(labelAssetType("food_beverages")).toBe(expiryWords[0].textContent);
    for (const category of taxonomy.plugins[0].categories) {
      expect(labelAssetType(category.id)).toBe(category.name);
    }
    expect(labelAssetType("unknown")).toBe("Uncategorized");
    expect(labelAssetType("product")).toBe("Product");
  });
});

describe("SG-307r1 fix 3: no Version text on the item panel", () => {
  function drawerAsset(): Asset {
    return {
      id: "asset-r1",
      household_id: "hh",
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
    };
  }

  test("the panel renders no Version text but keeps the value as data-version", async () => {
    const item = drawerAsset();
    client.apiGet.mockImplementation((path: string) =>
      path.includes("/v1/taxonomy")
        ? Promise.resolve(taxonomy)
        : Promise.resolve(item)
    );
    const { container } = providers(<ItemInspectorDrawer asset={item} householdId="hh" onClose={vi.fn()} />);
    await screen.findByTestId("inspector-drawer");
    expect(screen.queryByText(/Version/)).toBeNull();
    const hook = container.querySelector("[data-version]");
    expect(hook?.getAttribute("data-version")).toBe("1");
  });
});
