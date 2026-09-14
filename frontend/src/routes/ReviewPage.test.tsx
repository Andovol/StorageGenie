import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReviewPage } from "./ReviewPage";

const candidate = { id: "candidate-loaded-31", state: "proposed", job_id: "job-loaded-31", fields: { display_name: "Loaded item" }, dedup_matches: [], review_task_ids: [], evidence_ids: ["evidence-loaded-31"], asset_id: "asset-loaded-31" };
const api = vi.hoisted(() => ({ apiGet: vi.fn(), candidateDecision: vi.fn(), candidateSplit: vi.fn() }));
vi.mock("../api/client", () => api);

function renderPage() {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><MemoryRouter initialEntries={[`/review/${candidate.id}?household_id=household-loaded`]}><Routes><Route path="/review/:candidateId" element={<ReviewPage />} /></Routes></MemoryRouter></QueryClientProvider>);
}

afterEach(() => { vi.clearAllMocks(); });

describe("ReviewPage", () => {
  test("posts every decision with the loaded candidate id and supports keyboard actions", async () => {
    api.apiGet.mockImplementation((path: string) => path.startsWith("/v1/candidates/") ? Promise.resolve(candidate) : Promise.resolve({ id: "asset-loaded-31", assertions: [] }));
    api.candidateDecision.mockResolvedValue({ candidate_id: candidate.id, state: "held", asset_id: "asset-loaded-31" });
    renderPage();
    expect(await screen.findByDisplayValue("Loaded item")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Accept" }));
    fireEvent.click(screen.getByRole("button", { name: "Save edits" }));
    fireEvent.click(screen.getByRole("button", { name: "Hold / Unknown" }));
    fireEvent.click(screen.getByRole("button", { name: "Reject" }));
    fireEvent.keyDown(window, { key: "ArrowRight" });
    expect(await screen.findByTestId("keyboard-action")).toHaveTextContent("next");
    fireEvent.keyDown(window, { key: "a" });
    await waitFor(() => expect(api.candidateDecision).toHaveBeenCalledWith(candidate.id, "household-loaded", expect.anything(), expect.anything()));
    expect(api.candidateDecision.mock.calls.map((call) => call[0])).toEqual([candidate.id, candidate.id, candidate.id, candidate.id, candidate.id]);
  });

  test("wrong candidate fixture is discriminated by the loaded evidence id", async () => {
    api.apiGet.mockResolvedValue({ ...candidate, evidence_ids: ["wrong-evidence"] });
    renderPage();
    await screen.findByDisplayValue("Loaded item");
    expect(() => expect(screen.getByRole("article").querySelector("img")).toHaveAttribute("src", expect.stringContaining("evidence-loaded-31"))).toThrow();
  });

  test("multi-item task reveals the split action and presents the children after split", async () => {
    const task = { id: "task-multi-1", task_type: "candidate.multi_item", priority: "high", subject_ref: candidate.id, proposed_change: { candidate_id: candidate.id, item_count: 2 }, status: "open", household_id: "household-loaded", created_at: null, updated_at: null };
    api.apiGet.mockImplementation((path: string) => {
      if (path.startsWith("/v1/candidates/")) return Promise.resolve({ ...candidate, review_task_ids: [task.id] });
      if (path.startsWith("/v1/review-tasks")) return Promise.resolve({ items: [task], next_cursor: null, total: 1 });
      return Promise.resolve({});
    });
    api.candidateSplit.mockResolvedValue({ candidate_id: candidate.id, state: "split", resolved_task_ids: [task.id], children: [
      { id: "child-a", state: "proposed", job_id: candidate.job_id, fields: { display_name: { value: "Milk" } }, evidence_ids: ["evidence-loaded-31"] },
      { id: "child-b", state: "proposed", job_id: candidate.job_id, fields: { display_name: { value: "Yogurt" } }, evidence_ids: ["evidence-loaded-31"] },
    ] });
    renderPage();
    await screen.findByDisplayValue("Loaded item");
    fireEvent.click(await screen.findByRole("button", { name: /split/i }));
    await waitFor(() => expect(api.candidateSplit).toHaveBeenCalledWith(candidate.id, "household-loaded", [0, 1]));
    const milkLink = await screen.findByRole("link", { name: "Milk" });
    expect(milkLink.getAttribute("href") || "").toContain("/review/child-a");
    expect(screen.getByRole("link", { name: "Yogurt" })).toBeInTheDocument();
  });

  test("split rejection surfaces an alert", async () => {
    const task = { id: "task-multi-2", task_type: "candidate.multi_item", priority: "high", subject_ref: candidate.id, proposed_change: { candidate_id: candidate.id, item_count: 2 }, status: "open", household_id: "household-loaded", created_at: null, updated_at: null };
    api.apiGet.mockImplementation((path: string) => {
      if (path.startsWith("/v1/candidates/")) return Promise.resolve({ ...candidate, review_task_ids: [task.id] });
      if (path.startsWith("/v1/review-tasks")) return Promise.resolve({ items: [task], next_cursor: null, total: 1 });
      return Promise.resolve({});
    });
    api.candidateSplit.mockRejectedValue(new Error("split failed"));
    renderPage();
    await screen.findByDisplayValue("Loaded item");
    fireEvent.click(await screen.findByRole("button", { name: /split/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent("split failed");
  });
});
