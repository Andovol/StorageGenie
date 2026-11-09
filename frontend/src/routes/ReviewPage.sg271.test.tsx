import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReviewPage } from "./ReviewPage";

const base = { id: "candidate-271", state: "proposed", job_id: "job-271", fields: { display_name: "Loaded item" }, dedup_matches: [], review_task_ids: [], blocking_review_task_ids: [], evidence_ids: ["evidence-271"], asset_id: null };
const api = vi.hoisted(() => ({ apiGet: vi.fn(), candidateDecision: vi.fn(), candidateSplit: vi.fn(), classifyAsset: vi.fn() }));
vi.mock("../api/client", () => api);

function renderPage() {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><MemoryRouter initialEntries={[`/review/${base.id}?household_id=household-271`]}><Routes><Route path="/review/:candidateId" element={<ReviewPage />} /></Routes></MemoryRouter></QueryClientProvider>);
}

afterEach(() => { vi.clearAllMocks(); });

describe("ReviewPage SG-271", () => {
  test("a committed candidate reads In your catalog with an Open item link and no decisions", async () => {
    const committed = { ...base, state: "accepted", asset_id: "asset-271" };
    api.apiGet.mockImplementation((path: string) => path.startsWith("/v1/candidates/") ? Promise.resolve(committed) : Promise.resolve({ items: [], next_cursor: null, total: 0 }));
    renderPage();
    expect(await screen.findByText("In your catalog")).toBeInTheDocument();
    const link = screen.getByRole("link", { name: "Open item" });
    expect(link.getAttribute("href") || "").toContain("/assets/asset-271");
    expect(screen.queryByRole("button", { name: "Accept" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Save edits" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Hold / Unknown" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Reject" })).not.toBeInTheDocument();
    fireEvent.keyDown(window, { key: "a" });
    fireEvent.keyDown(window, { key: "r" });
    expect(api.candidateDecision).not.toHaveBeenCalled();
  });

  test("a fresh accept shows the AI shelf-life suggestion with one Confirm action", async () => {
    const undecided = { ...base, fields: { display_name: "Loaded item", category_proposed: { value: "food_beverages", confidence: 0.9, source_type: "extraction" } } };
    let reads = 0;
    api.apiGet.mockImplementation((path: string) => {
      if (!path.startsWith("/v1/candidates/")) return Promise.resolve({ items: [], next_cursor: null, total: 0 });
      reads += 1;
      return Promise.resolve(reads === 1 ? undecided : { ...undecided, state: "accepted", asset_id: "asset-271-new" });
    });
    api.candidateDecision.mockResolvedValue({ candidate_id: base.id, state: "accepted", asset_id: "asset-271-new", status: "committed", created: true });
    api.classifyAsset.mockResolvedValue({ classification: { category: "food_beverages" } });
    renderPage();
    fireEvent.click(await screen.findByRole("button", { name: "Accept" }));
    expect(await screen.findByText("In your catalog")).toBeInTheDocument();
    expect(screen.getByText(/The AI suggests/)).toHaveTextContent("food_beverages");
    fireEvent.click(screen.getByRole("button", { name: "Confirm shelf life" }));
    await waitFor(() => expect(api.classifyAsset).toHaveBeenCalledWith("asset-271-new", "household-271", "food_beverages"));
    expect(await screen.findByText("Shelf life saved — see it on the item page.")).toBeInTheDocument();
  });
});
