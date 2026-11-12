import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { InboxPage } from "./InboxPage";
import { HouseholdProvider } from "../hooks/HouseholdContext";

const household = { id: "household-271", name: "SG-271 home", created_at: "2026-01-01" };
const job = { id: "job-271a", job_type: "import", state: "AWAITING_REVIEW", household_id: household.id, created_at: null, updated_at: null };

const api = vi.hoisted(() => ({ apiGet: vi.fn(), apiPost: vi.fn(), resolveReviewTask: vi.fn() }));
vi.mock("../api/client", () => api);
vi.mock("../hooks/useAssets", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../hooks/useAssets")>()),
  useHouseholds: () => ({ data: [household] }),
}));

function renderPage() {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><HouseholdProvider><MemoryRouter><InboxPage /></MemoryRouter></HouseholdProvider></QueryClientProvider>);
}

afterEach(() => { vi.clearAllMocks(); });

describe("InboxPage SG-271", () => {
  test("a committed candidate links to its item, not to Review", async () => {
    const committed = { id: "candidate-271-c", state: "accepted", job_id: job.id, fields: { display_name: { value: "Milk carton" } }, evidence_ids: ["ev-271"], review_task_ids: [], asset_id: "asset-271-c" };
    const pending = { id: "candidate-271-p", state: "proposed", job_id: job.id, fields: { display_name: { value: "Soup tin" } }, evidence_ids: ["ev-271"], review_task_ids: [] };
    const detail = { ...job, steps: [], progress: { completed: 2, total: 2, failed: 0, pending: 0 }, errors: [] };
    api.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/jobs") return Promise.resolve({ items: [job], next_cursor: null, total: 1 });
      if (path === `/v1/imports/${job.id}`) return Promise.resolve(detail);
      if (path === `/v1/jobs/${job.id}/candidates`) return Promise.resolve({ items: [committed, pending], total: 2 });
      return Promise.resolve({ items: [], next_cursor: null, total: 0 });
    });
    renderPage();
    fireEvent.click(await screen.findByText("Import job"));
    expect(await screen.findByText("Milk carton")).toBeInTheDocument();
    const openItem = await screen.findByRole("link", { name: "Open item" });
    expect(openItem.getAttribute("href") || "").toContain("/assets/asset-271-c");
    const review = await screen.findByRole("link", { name: "Review" });
    expect(review.getAttribute("href") || "").toContain("/review/candidate-271-p");
  });

  test("a skipped step reads Skipped (AI off)", async () => {
    const detail = {
      ...job,
      steps: [{ id: "step-271", step_name: "ANALYZING_WITH_AI", state: "COMPLETED", attempts: 1, input: null, output: { status: "skipped", reason: "consent_disabled" }, error: null }],
      progress: { completed: 2, total: 6, failed: 0, pending: 4 },
      errors: [],
    };
    api.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/jobs") return Promise.resolve({ items: [job], next_cursor: null, total: 1 });
      if (path === `/v1/imports/${job.id}`) return Promise.resolve(detail);
      return Promise.resolve({ items: [], next_cursor: null, total: 0 });
    });
    renderPage();
    fireEvent.click(await screen.findByText("Import job"));
    // SG-301 G2: the skipped step reads "Skipped (AI off)" (labelStepStatus),
    // never the old consent sentence and never Done.
    expect(await screen.findByText("Skipped (AI off)", { exact: false })).toBeInTheDocument();
  });
});
