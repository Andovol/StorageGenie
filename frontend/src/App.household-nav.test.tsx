import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";
import { ThemeProvider } from "./theme/ThemeProvider";
import type { ReviewTask } from "./api/types";

/**
 * SG-196: one shared household context mounted at App level. SG-208/D-13: the
 * household SWITCHING controls are gone — these rows assert the ABSENCE of any
 * household combobox while the resolution rail (stored id else first household,
 * auto-persisted) keeps scoping the reads. The nav keeps its household failure
 * alert and the Inbox open-task badge; Catalog keeps its facets/saved-search
 * alerts. Only ../api/client is mocked, so the real hooks, context and query
 * wiring run.
 *
 * Non-vacuity (PB-3): each absence row first pins content that DOES render on
 * the same DOM (the nav footer, the Inbox review-status combobox) or a scoped
 * read fired by the page, so the role query is proven live and the row cannot
 * pass by never looking.
 */
const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPatch: vi.fn(),
  buildUrl: (path: string) => path,
  fetchAiSettings: vi.fn(),
  updateAiModel: vi.fn(),
}));
vi.mock("./api/client", () => api);

const homeA = { id: "hh-a", name: "Home A", created_at: "2026-01-01" };
const homeB = { id: "hh-b", name: "Home B", created_at: "2026-01-01" };
const emptyList = { items: [], next_cursor: null, total: 0 };
const pending = () => new Promise<never>(() => undefined);

function reviewTask(id: string, status: string): ReviewTask {
  return {
    id,
    task_type: "identifier_collision",
    priority: "high",
    subject_ref: `cand-${id}`,
    proposed_change: null,
    status,
    household_id: homeA.id,
    created_at: null,
    updated_at: null,
  };
}

type Overrides = Record<string, () => Promise<unknown>>;

function mockApiGet(overrides: Overrides = {}) {
  api.apiGet.mockImplementation((path: string) => {
    const handler = overrides[path];
    if (handler) return handler();
    if (path === "/v1/households") return Promise.resolve([homeA, homeB]);
    if (path === "/v1/review-tasks") return Promise.resolve(emptyList);
    if (path === "/v1/jobs") return Promise.resolve(emptyList);
    if (path === "/v1/assets") return Promise.resolve(emptyList);
    if (path === "/v1/assets/facets")
      return Promise.resolve({ asset_type: {}, status: {}, has_evidence: {} });
    if (path === "/v1/saved-searches") return Promise.resolve(emptyList);
    return Promise.resolve(emptyList);
  });
}

function renderApp(initialEntries: string[] = ["/settings"]) {
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

function householdComboboxes(): HTMLElement[] {
  return screen.queryAllByRole("combobox", { name: /household/i }) as HTMLElement[];
}

beforeEach(() => {
  window.localStorage.clear();
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
  mockApiGet();
});

afterEach(() => {
  vi.clearAllMocks();
});

describe("SG-196 shared household context / SG-208 no switching UI", () => {
  test("the nav carries no household control; the first household is resolved and persisted (A1)", async () => {
    renderApp();

    // Non-vacuity: the nav itself rendered (its footer), then the absence row.
    expect(await screen.findByText("Phase 0 · local-first")).toBeInTheDocument();
    await waitFor(() => expect(window.localStorage.getItem("household_id")).toBe("hh-a"));
    expect(householdComboboxes()).toHaveLength(0);
    const householdCalls = api.apiGet.mock.calls.filter(([path]) => path === "/v1/households");
    expect(householdCalls).toHaveLength(1);
  });

  test("a stored household_id scopes every read; no route renders a household control (A1)", async () => {
    window.localStorage.setItem("household_id", "hh-b");
    renderApp(["/inbox"]);

    await waitFor(() =>
      expect(
        api.apiGet.mock.calls.some(
          ([path, params]) =>
            path === "/v1/jobs" &&
            (params as { household_id?: string } | undefined)?.household_id === "hh-b"
        )
      ).toBe(true)
    );
    // Non-vacuity: the Inbox's own review-status combobox renders (the role
    // query is live on this DOM); the household matcher finds nothing and the
    // stored id survives untouched.
    expect(await screen.findByRole("combobox", { name: /review status/i })).toBeInTheDocument();
    expect(householdComboboxes()).toHaveLength(0);
    expect(window.localStorage.getItem("household_id")).toBe("hh-b");
  });

  test("a failed households read alerts in the nav (G1)", async () => {
    mockApiGet({ "/v1/households": () => Promise.reject(new Error("households read failed")) });
    renderApp();

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not load households");
    expect(alert).toHaveTextContent("households read failed");
    expect(householdComboboxes()).toHaveLength(0);
  });

  test("(control) a loaded households read renders no nav alert", async () => {
    renderApp(["/inbox"]);

    await waitFor(() => expect(window.localStorage.getItem("household_id")).toBe("hh-a"));
    expect(screen.queryByRole("alert")).toBeNull();
    expect(householdComboboxes()).toHaveLength(0);
  });
});

describe("SG-196 nav Inbox badge (G3)", () => {
  test("the badge shows the loaded open-task count and the accessible name carries it", async () => {
    mockApiGet({
      "/v1/review-tasks": () =>
        Promise.resolve({
          items: [reviewTask("t1", "open"), reviewTask("t2", "open"), reviewTask("t3", "resolved")],
          next_cursor: null,
          total: 3,
        }),
    });
    renderApp();

    const link = await screen.findByRole("link", { name: "Inbox, 2 open review tasks" });
    expect(within(link).getByTestId("inbox-open-count")).toHaveTextContent("2");
  });

  test("a loaded zero-task read renders the honest zero badge, never a hidden count", async () => {
    mockApiGet({
      "/v1/review-tasks": () =>
        Promise.resolve({ items: [reviewTask("t1", "resolved")], next_cursor: null, total: 1 }),
    });
    renderApp();

    const link = await screen.findByRole("link", { name: "Inbox, 0 open review tasks" });
    expect(within(link).getByTestId("inbox-open-count")).toHaveTextContent("0");
  });

  test("(control) a failed review-tasks read renders no badge", async () => {
    mockApiGet({ "/v1/review-tasks": () => Promise.reject(new Error("tasks read failed")) });
    renderApp(["/inbox"]);

    // The Inbox route's own SG-195 alert proves the shared read reached its
    // error state on both trees; the nav must show no badge and no zero.
    const inboxAlert = await screen.findByRole("alert");
    expect(inboxAlert).toHaveTextContent("Could not load review tasks");
    expect(screen.queryByTestId("inbox-open-count")).toBeNull();
    expect(screen.getByRole("link", { name: "Inbox" })).toBeInTheDocument();
  });

  test("(control) a pending review-tasks read renders no badge", async () => {
    mockApiGet({ "/v1/review-tasks": () => pending() });
    renderApp(["/inbox"]);

    await waitFor(() =>
      expect(api.apiGet.mock.calls.some(([path]) => path === "/v1/review-tasks")).toBe(true)
    );
    // Still loading: the loaded-empty copy is withheld, and the nav badge is absent.
    expect(screen.queryByText("No review tasks.")).toBeNull();
    expect(screen.queryByTestId("inbox-open-count")).toBeNull();
    expect(screen.getByRole("link", { name: "Inbox" })).toBeInTheDocument();
  });

  test("(control) no household renders no badge and requests no tasks", async () => {
    mockApiGet({ "/v1/households": () => Promise.resolve([]) });
    renderApp();

    await waitFor(() =>
      expect(api.apiGet.mock.calls.some(([path]) => path === "/v1/households")).toBe(true)
    );
    await waitFor(() => expect(screen.queryByTestId("inbox-open-count")).toBeNull());
    expect(api.apiGet.mock.calls.some(([path]) => path === "/v1/review-tasks")).toBe(false);
    expect(screen.getByRole("link", { name: "Inbox" })).toBeInTheDocument();
    expect(householdComboboxes()).toHaveLength(0);
  });
});

describe("SG-196 Catalog household-adjacent alerts (G2)", () => {
  test("a failed facets read alerts naming the facets", async () => {
    mockApiGet({ "/v1/assets/facets": () => Promise.reject(new Error("facets read failed")) });
    renderApp(["/"]);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not load catalog facets");
    expect(alert).toHaveTextContent("facets read failed");
  });

  test("a failed saved-searches read alerts naming the saved searches", async () => {
    mockApiGet({ "/v1/saved-searches": () => Promise.reject(new Error("saved searches read failed")) });
    renderApp(["/"]);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not load saved searches");
    expect(alert).toHaveTextContent("saved searches read failed");
  });

  test("(control) the loaded Catalog path renders neither alert", async () => {
    renderApp(["/"]);

    expect(await screen.findByText("No items match the current view.")).toBeInTheDocument();
    expect(screen.queryByRole("alert")).toBeNull();
    expect(householdComboboxes()).toHaveLength(0);
  });
});
