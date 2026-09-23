import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactElement } from "react";
import App from "../App";
import { ThemeProvider } from "../theme/ThemeProvider";
import { AssetDetailPage } from "./AssetDetailPage";
import { AnalyticsPage } from "./AnalyticsPage";
import { CapturePage } from "./CapturePage";
import { ChatPage } from "./ChatPage";
import { InboxPage } from "./InboxPage";
import { PlanningPage } from "./PlanningPage";
import { ReviewPage } from "./ReviewPage";
import { SettingsPage } from "./SettingsPage";

/**
 * SG-075: per-screen adoption proof. Every landmark assertion here is a
 * token-class check on a screen that previously rendered unstyled browser
 * defaults. These MUST fail before the migration and pass after.
 *
 * The hook mocks return STABLE object identities on every render; returning
 * fresh objects makes CatalogPage's accumulation effect re-fire forever.
 */

const fixtures = vi.hoisted(() => {
  const household = { id: "hh-theme", name: "Theme home", created_at: "2026-01-01" };
  const asset = {
    id: "asset-theme",
    household_id: "hh-theme",
    display_name: "Theme asset",
    asset_type: "product",
    status: "ACTIVE",
    quantity: 1,
    unit: "pc",
    condition: null,
    version: 1,
    created_at: "2026-01-01T00:00:00+00:00",
    updated_at: null,
    evidence: [],
    assertions: [],
    audit_events: [],
  };
  const candidate = {
    id: "cand-theme",
    household_id: "hh-theme",
    job_id: "job-theme",
    state: "PROPOSED",
    fields: { display_name: "Theme candidate" },
    dedup_matches: [],
    evidence_ids: [],
    review_task_ids: [],
    asset_id: null,
    created_at: null,
    updated_at: null,
  };
  const noop = () => undefined;
  const hooks = {
    households: { data: [household] },
    assets: { data: { items: [], next_cursor: null }, isLoading: false, isFetching: false },
    facets: { data: { asset_type: {} } },
    savedSearches: { data: { items: [] } },
    saveSearch: { mutate: noop },
    deleteSavedSearch: { mutate: noop },
    asset: { data: asset, isLoading: false },
    taxonomy: { data: { plugins: [] } },
  };
  return { household, asset, candidate, hooks };
});

const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPatch: vi.fn(),
  apiPut: vi.fn(),
  buildUrl: vi.fn(),
  uploadEvidence: vi.fn(),
  fetchAiSettings: vi.fn(),
  updateAiModel: vi.fn(),
  fetchAnalyticsSummary: vi.fn(),
  generateAnalyticsInsights: vi.fn(),
  enterManualExpiry: vi.fn(),
  sendChat: vi.fn(),
  logChatCorrection: vi.fn(),
  runPlanning: vi.fn(),
  fetchPlanningSuggestions: vi.fn(),
  confirmPlanningSuggestion: vi.fn(),
  dismissPlanningSuggestion: vi.fn(),
  candidateDecision: vi.fn(),
  candidateSplit: vi.fn(),
  resolveReviewTask: vi.fn(),
}));
vi.mock("../api/client", () => api);

vi.mock("../hooks/useAssets", () => ({
  useHouseholds: () => fixtures.hooks.households,
  useAssets: () => fixtures.hooks.assets,
  useFacets: () => fixtures.hooks.facets,
  useSavedSearches: () => fixtures.hooks.savedSearches,
  useSaveSearch: () => fixtures.hooks.saveSearch,
  useDeleteSavedSearch: () => fixtures.hooks.deleteSavedSearch,
  useAsset: () => fixtures.hooks.asset,
  useTaxonomy: () => fixtures.hooks.taxonomy,
}));

function renderWithProviders(ui: ReactElement, initialEntries: string[] = ["/"]) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ThemeProvider>
        <MemoryRouter initialEntries={initialEntries}>{ui}</MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

beforeEach(() => {
  window.localStorage.clear();
  document.documentElement.className = "";
  api.apiGet.mockReset();
  api.fetchAiSettings.mockResolvedValue({
    provider_id: "fake",
    model_id: "m1",
    allowed_model_ids: ["m1"],
    consent: false,
    per_job_cap: null,
    monthly_cap: null,
    prompt_category: "food",
  });
  api.fetchAnalyticsSummary.mockResolvedValue({
    household_id: "hh-theme",
    as_of_date: "2026-09-21",
    generated_at: "2026-09-21T00:00:00+00:00",
    assets: { total: 0, active: 0, by_status: {} },
    categories: { taxonomy: [], counts: {}, uncategorized: 0 },
    expiry: { expired: 0, within_7_days: 0, within_30_days: 0, safe: 0, unknown: 0 },
    waste: { expired_untouched: 0 },
    adherence: { suggestions: { pending: 0, confirmed: 0, dismissed: 0 }, review_tasks: { open: 0, resolved: 0 } },
    stats: [],
  });
  api.fetchPlanningSuggestions.mockResolvedValue({ items: [], next_cursor: null, total: 0 });
  api.apiGet.mockImplementation((path: string) => {
    if (path === "/v1/jobs") return Promise.resolve({ items: [], next_cursor: null, total: 0 });
    if (path === "/v1/review-tasks") return Promise.resolve({ items: [], next_cursor: null, total: 0 });
    if (path.startsWith("/v1/candidates/")) return Promise.resolve(fixtures.candidate);
    return Promise.resolve(null);
  });
});

afterEach(() => {
  vi.clearAllMocks();
});

function expectPageHeader(name: RegExp) {
  const heading = screen.getByRole("heading", { level: 1, name });
  expect(heading).toHaveClass("page-header");
  expect(heading).toHaveClass("text-foreground");
}

describe("SG-075 screen adoption", () => {
  test("App nav carries the card/border tokens and surfaces the theme toggle", () => {
    renderWithProviders(<App />);
    const nav = document.querySelector("nav");
    expect(nav).not.toBeNull();
    expect(nav).toHaveClass("bg-card");
    expect(nav).toHaveClass("border-border");
    expect(screen.getByRole("button", { name: /switch to .* theme/i })).toBeInTheDocument();
  });

  test("analytics screen header is token-styled", async () => {
    renderWithProviders(<AnalyticsPage />);
    expectPageHeader(/analytics/i);
  });

  test("asset detail screen header is token-styled", async () => {
    renderWithProviders(
      <Routes>
        <Route path="/assets/:id" element={<AssetDetailPage />} />
      </Routes>,
      ["/assets/asset-theme?household_id=hh-theme"]
    );
    expectPageHeader(/theme asset/i);
  });

  test("capture screen header is token-styled", () => {
    renderWithProviders(<CapturePage />);
    expectPageHeader(/capture/i);
  });

  test("chat screen header is token-styled", () => {
    renderWithProviders(<ChatPage />);
    expectPageHeader(/chat/i);
  });

  test("inbox screen header is token-styled", async () => {
    renderWithProviders(<InboxPage />);
    expectPageHeader(/inbox/i);
  });

  test("planning screen header is token-styled", () => {
    renderWithProviders(<PlanningPage />);
    expectPageHeader(/planning/i);
  });

  test("review screen header is token-styled", async () => {
    renderWithProviders(
      <Routes>
        <Route path="/review/:candidateId" element={<ReviewPage />} />
      </Routes>,
      ["/review/cand-theme?household_id=hh-theme"]
    );
    expectPageHeader(/review workspace/i);
  });

  test("settings screen header is token-styled", () => {
    renderWithProviders(<SettingsPage />);
    expectPageHeader(/settings/i);
  });

  test("capture screen rides the shared centered container and themed household select (SG-105 G1/G2)", () => {
    const { container } = renderWithProviders(<CapturePage />);

    const page = container.querySelector(".page-container") as HTMLElement;
    expect(page).not.toBeNull();
    expect(page).toHaveStyle({ maxWidth: "1100px", marginLeft: "auto", marginRight: "auto" });

    const select = screen.getByRole("combobox", { name: /household/i });
    expect(select).toHaveClass("bg-background", "text-foreground", "border-border");
  });
});

describe("SG-075 theme toggle interaction", () => {
  test("clicking the nav toggle flips the document class and persists sg-theme", () => {
    renderWithProviders(<App />);
    fireEvent.click(screen.getByRole("button", { name: /switch to dark theme/i }));
    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(window.localStorage.getItem("sg-theme")).toBe("dark");
  });
});
