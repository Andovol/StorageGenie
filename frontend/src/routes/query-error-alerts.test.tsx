import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { AnalyticsPage } from "./AnalyticsPage";
import { CapturePage } from "./CapturePage";
import { CatalogPage } from "./CatalogPage";
import { InboxPage } from "./InboxPage";
import { PlanningPage } from "./PlanningPage";
import { ThemeProvider } from "../theme/ThemeProvider";
import type { AnalyticsSummary } from "../api/types";

/**
 * SG-195: every route in the SG-190 REMAINING set renders a named
 * role="alert" on a failed query instead of loading/empty text.
 * One focused module (not five) because the behaviour under test is the SAME
 * cross-route contract and the FAIL-then-PASS pair runs as one node set.
 * Only `../api/client` is mocked, so the real hooks and query wiring run.
 */
const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  buildUrl: (path: string) => path,
  resolveReviewTask: vi.fn(),
  fetchAnalyticsSummary: vi.fn(),
  generateAnalyticsInsights: vi.fn(),
  fetchPlanningSuggestions: vi.fn(),
  runPlanning: vi.fn(),
  confirmPlanningSuggestion: vi.fn(),
  dismissPlanningSuggestion: vi.fn(),
}));
vi.mock("../api/client", () => api);

const household = { id: "hh-sg195", name: "Error home", created_at: "2026-01-01" };
const emptyList = { items: [], next_cursor: null, total: 0 };
const pending = () => new Promise<never>(() => undefined);

const emptySummary: AnalyticsSummary = {
  household_id: household.id,
  as_of_date: "2026-10-16",
  generated_at: "2026-10-16T00:00:00+00:00",
  assets: { total: 0, active: 0, by_status: {} },
  categories: { taxonomy: [], counts: {}, uncategorized: 0 },
  expiry: { expired: 0, within_7_days: 0, within_30_days: 0, safe: 0, unknown: 0 },
  waste: { expired_untouched: 0 },
  adherence: {
    suggestions: { pending: 0, confirmed: 0, dismissed: 0 },
    review_tasks: { open: 0, resolved: 0 },
  },
  stats: [],
};

function catalogApiGet(assets: () => Promise<unknown>) {
  api.apiGet.mockImplementation((path: string) => {
    if (path === "/v1/households") return Promise.resolve([household]);
    if (path === "/v1/assets") return assets();
    if (path === "/v1/assets/facets")
      return Promise.resolve({ asset_type: {}, status: {}, has_evidence: {} });
    if (path === "/v1/saved-searches") return Promise.resolve(emptyList);
    return Promise.resolve(emptyList);
  });
}

function inboxApiGet(
  jobs: () => Promise<unknown>,
  tasks: () => Promise<unknown>,
  detail: () => Promise<unknown>
) {
  api.apiGet.mockImplementation((path: string) => {
    if (path === "/v1/households") return Promise.resolve([household]);
    if (path === "/v1/jobs") return jobs();
    if (path === "/v1/review-tasks") return tasks();
    if (path.startsWith("/v1/imports/")) return detail();
    return Promise.resolve(emptyList);
  });
}

function renderPage(node: ReactNode) {
  return render(
    <MemoryRouter>
      <ThemeProvider>
        <QueryClientProvider
          client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
        >
          {node}
        </QueryClientProvider>
      </ThemeProvider>
    </MemoryRouter>
  );
}

afterEach(() => {
  vi.clearAllMocks();
});

beforeEach(() => {
  localStorage.clear();
});

describe("SG-195 route query-error alerts", () => {
  test("Catalog: a failed asset-list query alerts naming the list and hides the empty view", async () => {
    catalogApiGet(() => Promise.reject(new Error("asset list read failed")));
    renderPage(<CatalogPage />);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not load the asset list");
    expect(alert).toHaveTextContent("asset list read failed");
    expect(screen.queryByText("No items match the current view.")).not.toBeInTheDocument();
  });

  test("Catalog: the loaded empty path keeps its empty view with no alert", async () => {
    catalogApiGet(() => Promise.resolve(emptyList));
    renderPage(<CatalogPage />);

    expect(await screen.findByText("No items match the current view.")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  test("Catalog: the loading path still shows the skeleton, not an alert", async () => {
    catalogApiGet(pending);
    renderPage(<CatalogPage />);

    expect(await screen.findByTestId("catalog-grid")).toHaveAttribute("aria-busy", "true");
    expect(screen.queryByRole("alert")).toBeNull();
  });

  test("Capture: a failed household query alerts and never claims an unseeded database", async () => {
    api.apiGet.mockImplementation((path: string) =>
      path === "/v1/households"
        ? Promise.reject(new Error("households read failed"))
        : Promise.resolve(emptyList)
    );
    renderPage(<CapturePage />);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not load households");
    expect(alert).toHaveTextContent("households read failed");
    expect(
      screen.queryByText("No household available — seed the database first.")
    ).not.toBeInTheDocument();
  });

  test("Capture: the loaded empty household list keeps its empty text with no alert", async () => {
    api.apiGet.mockResolvedValue([]);
    renderPage(<CapturePage />);

    expect(
      await screen.findByText("No household available — seed the database first.")
    ).toBeInTheDocument();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  test("Analytics: a failed summary query alerts naming the summary", async () => {
    api.apiGet.mockResolvedValue([household]);
    api.fetchAnalyticsSummary.mockRejectedValue(new Error("summary read failed"));
    renderPage(<AnalyticsPage />);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not load the analytics summary");
    expect(alert).toHaveTextContent("summary read failed");
  });

  test("Analytics: the summary empty path stays with no alert", async () => {
    api.apiGet.mockResolvedValue([household]);
    api.fetchAnalyticsSummary.mockResolvedValue(emptySummary);
    renderPage(<AnalyticsPage />);

    expect(
      await screen.findByText("No analytics data yet for this household.")
    ).toBeInTheDocument();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  test("Analytics: the loading path still shows its loading copy, not an alert", async () => {
    api.apiGet.mockResolvedValue([household]);
    api.fetchAnalyticsSummary.mockImplementation(pending);
    renderPage(<AnalyticsPage />);

    expect(await screen.findByText("Loading analytics…")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  test("Planning: a failed household query alerts and suggestions stay unrequested", async () => {
    api.apiGet.mockImplementation((path: string) =>
      path === "/v1/households"
        ? Promise.reject(new Error("households read failed"))
        : Promise.resolve(emptyList)
    );
    api.fetchPlanningSuggestions.mockResolvedValue(emptyList);
    renderPage(<PlanningPage />);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not load households");
    expect(alert).toHaveTextContent("households read failed");
    expect(api.fetchPlanningSuggestions).not.toHaveBeenCalled();
  });

  test("Planning: a failed suggestions query alerts naming the suggestions", async () => {
    api.apiGet.mockResolvedValue([household]);
    api.fetchPlanningSuggestions.mockRejectedValue(new Error("suggestions read failed"));
    renderPage(<PlanningPage />);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not load planning suggestions");
    expect(alert).toHaveTextContent("suggestions read failed");
  });

  test("Planning: the suggestions empty path stays with no alert", async () => {
    api.apiGet.mockResolvedValue([household]);
    api.fetchPlanningSuggestions.mockResolvedValue(emptyList);
    renderPage(<PlanningPage />);

    expect(await screen.findByText("No planning suggestions yet.")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  test("Planning: the loading path still shows its loading copy, not an alert", async () => {
    api.apiGet.mockResolvedValue([household]);
    api.fetchPlanningSuggestions.mockImplementation(pending);
    renderPage(<PlanningPage />);

    expect(await screen.findByText("Loading suggestions…")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  test("Inbox: a failed jobs query alerts naming import jobs", async () => {
    inboxApiGet(
      () => Promise.reject(new Error("jobs read failed")),
      () => Promise.resolve(emptyList),
      pending
    );
    renderPage(<InboxPage />);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not load import jobs");
    expect(alert).toHaveTextContent("jobs read failed");
  });

  test("Inbox: a failed review-tasks query alerts naming review tasks", async () => {
    inboxApiGet(
      () => Promise.resolve(emptyList),
      () => Promise.reject(new Error("tasks read failed")),
      pending
    );
    renderPage(<InboxPage />);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not load review tasks");
    expect(alert).toHaveTextContent("tasks read failed");
  });

  test("Inbox: a failed job-detail query alerts naming the detail", async () => {
    const job = {
      id: "jobquery195",
      job_type: "import",
      state: "CREATED",
      household_id: household.id,
      created_at: null,
      updated_at: null,
    };
    inboxApiGet(
      () => Promise.resolve({ items: [job], next_cursor: null, total: 1 }),
      () => Promise.resolve(emptyList),
      () => Promise.reject(new Error("detail read failed"))
    );
    renderPage(<InboxPage />);

    fireEvent.click(await screen.findByText("Import jobquery"));
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not load job detail");
    expect(alert).toHaveTextContent("detail read failed");
  });

  test("Inbox: the loaded empty paths stay with no alert", async () => {
    inboxApiGet(
      () => Promise.resolve(emptyList),
      () => Promise.resolve(emptyList),
      pending
    );
    renderPage(<InboxPage />);

    expect(await screen.findByText("No import jobs yet.")).toBeInTheDocument();
    expect(await screen.findByText("No review tasks.")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  test("Inbox: the loading path still shows its loading copy, not an alert", async () => {
    inboxApiGet(pending, () => Promise.resolve(emptyList), pending);
    renderPage(<InboxPage />);

    expect(await screen.findByText("Loading jobs…")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).toBeNull();
  });
});
