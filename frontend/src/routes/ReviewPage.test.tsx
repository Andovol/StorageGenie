import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReviewPage } from "./ReviewPage";

const candidate = { id: "candidate-loaded-31", state: "proposed", job_id: "job-loaded-31", fields: { display_name: "Loaded item" }, dedup_matches: [], review_task_ids: [], evidence_ids: ["evidence-loaded-31"], asset_id: "asset-loaded-31" };
const api = vi.hoisted(() => ({ apiGet: vi.fn(), candidateDecision: vi.fn() }));
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
});
