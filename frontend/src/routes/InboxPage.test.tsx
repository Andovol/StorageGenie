import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { InboxPage } from "./InboxPage";

const household = { id: "household-loaded", name: "Loaded home", created_at: "2026-01-01" };
const job = { id: "job-loaded-91", job_type: "import", state: "FAILED", household_id: household.id, created_at: null, updated_at: null };
const detail = { ...job, steps: [{ id: "step-loaded", step_name: "EXTRACTING", state: "FAILED", attempts: 1, input: null, output: { error: "decoder failed on loaded image" }, error: "decoder failed on loaded image" }], progress: { completed: 2, total: 6, failed: 1, pending: 3 }, errors: ["decoder failed on loaded image"] };

const api = vi.hoisted(() => ({ apiGet: vi.fn(), apiPost: vi.fn(), resolveReviewTask: vi.fn() }));
vi.mock("../api/client", () => api);
vi.mock("../hooks/useAssets", () => ({ useHouseholds: () => ({ data: [household] }) }));

function renderPage() {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><MemoryRouter><InboxPage /></MemoryRouter></QueryClientProvider>);
}

afterEach(() => { vi.clearAllMocks(); });

describe("InboxPage", () => {
  test("renders failed loaded job detail and retries that loaded id", async () => {
    api.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/jobs") return Promise.resolve({ items: [job], next_cursor: null, total: 1 });
      if (path === `/v1/imports/${job.id}`) return Promise.resolve(detail);
      return Promise.resolve({ items: [], next_cursor: null, total: 0 });
    });
    api.apiPost.mockResolvedValue({ ...detail, state: "AWAITING_REVIEW" });
    renderPage();
    fireEvent.click(await screen.findByText("Import job-load"));
    expect((await screen.findAllByText("decoder failed on loaded image")).length).toBeGreaterThan(0);
    const retry = await screen.findByRole("button", { name: "Retry failed job" });
    expect(retry).toBeEnabled();
    fireEvent.click(retry);
    await waitFor(() => expect(api.apiPost).toHaveBeenCalledWith(`/v1/imports/${job.id}/retry`, {}, { household_id: household.id }));
  });

  test("shows both loaded empty states", async () => {
    api.apiGet.mockResolvedValue({ items: [], next_cursor: null, total: 0 });
    renderPage();
    expect(await screen.findByText("No import jobs yet.")).toBeInTheDocument();
    expect(await screen.findByText("No review tasks.")).toBeInTheDocument();
  });

  test("lists a loaded review task and resolves its loaded id", async () => {
    const task = { id: "task-loaded-44", task_type: "identifier_collision", priority: "high", subject_ref: "candidate-loaded-44", proposed_change: null, status: "open", household_id: household.id, created_at: null, updated_at: null };
    api.apiGet.mockImplementation((path: string) => path === "/v1/jobs" ? Promise.resolve({ items: [], next_cursor: null, total: 0 }) : Promise.resolve({ items: [task], next_cursor: null, total: 1 }));
    api.resolveReviewTask.mockResolvedValue({ id: task.id, status: "resolved" });
    renderPage();
    expect(await screen.findByText("identifier_collision")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Resolve" }));
    await waitFor(() => expect(api.resolveReviewTask).toHaveBeenCalledWith(task.id, household.id));
  });

  test("wrong job fixture does not satisfy the loaded error property", async () => {
    api.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/jobs") return Promise.resolve({ items: [job], next_cursor: null, total: 1 });
      if (path === `/v1/imports/${job.id}`) return Promise.resolve({ ...detail, errors: ["wrong error"] });
      return Promise.resolve({ items: [], next_cursor: null, total: 0 });
    });
    renderPage();
    fireEvent.click(await screen.findByText("Import job-load"));
    await waitFor(() => expect(() => expect(screen.getByRole("alert")).toHaveTextContent("decoder failed on loaded image")).toThrow());
  });
});
