import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { InboxPage } from "../routes/InboxPage";

const household = { id: "h-probe", name: "Probe home", created_at: "2026-01-01" };
const created = { id: "job-created-probe", job_type: "import", state: "CREATED", household_id: household.id, created_at: null, updated_at: null };
const failed = { id: "job-failed-probe", job_type: "import", state: "FAILED", household_id: household.id, created_at: null, updated_at: null };

const api = vi.hoisted(() => ({ apiGet: vi.fn(), apiPost: vi.fn(), resolveReviewTask: vi.fn() }));
vi.mock("../api/client", () => api);
vi.mock("../hooks/useAssets", () => ({ useHouseholds: () => ({ data: [household] }) }));

function renderPage() {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><MemoryRouter><InboxPage /></MemoryRouter></QueryClientProvider>);
}

afterEach(() => { vi.clearAllMocks(); });

function mockJobs(job: typeof created) {
  api.apiGet.mockImplementation((path: string) => {
    if (path === "/v1/jobs") return Promise.resolve({ items: [job], next_cursor: null, total: 1 });
    if (path === `/v1/imports/${job.id}`) return Promise.resolve({ ...job, steps: [], progress: null, errors: [] });
    return Promise.resolve({ items: [], next_cursor: null, total: 0 });
  });
}

describe("SG-179 probe: CREATED import offers no run control (REC-ST03)", () => {
  test("CREATED job renders with no Run/Retry action while FAILED offers Retry (working control)", async () => {
    mockJobs(created);
    const view = renderPage();
    fireEvent.click(await screen.findByText("Import job-crea"));
    await waitFor(() => expect(screen.getByText("CREATED")).toBeInTheDocument());
    expect(screen.queryByRole("button", { name: /run|start/i })).toBeNull();
    expect(screen.queryByRole("button", { name: "Retry failed job" })).toBeNull();

    view.unmount();
    mockJobs(failed);
    renderPage();
    fireEvent.click(await screen.findByText("Import job-fail"));
    const retry = await screen.findByRole("button", { name: "Retry failed job" });
    expect(retry).toBeEnabled();
  });
});
