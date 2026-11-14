import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReviewPage } from "./ReviewPage";

// SG-304 G2 (F10): the review page names the existing item and sends each choice.
const ASSET_ID = "asset-olive-304";
const NEW_ASSET_ID = "asset-new-304";
const candidate = {
  id: "candidate-304",
  state: "proposed",
  job_id: "job-304",
  fields: { display_name: "Olive Oil" },
  dedup_matches: [{ type: "duplicate_of_asset", asset_id: ASSET_ID }],
  review_task_ids: [],
  blocking_review_task_ids: [],
  evidence_ids: ["evidence-304"],
  asset_id: null,
};
const api = vi.hoisted(() => ({ apiGet: vi.fn(), candidateDecision: vi.fn(), candidateSplit: vi.fn() }));
vi.mock("../api/client", () => api);

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={[`/review/${candidate.id}?household_id=hh-304`]}>
        <Routes>
          <Route path="/review/:candidateId" element={<ReviewPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

function serve() {
  api.apiGet.mockImplementation((path: string) => {
    if (path.startsWith("/v1/candidates/")) return Promise.resolve(candidate);
    if (path === `/v1/assets/${ASSET_ID}`) {
      return Promise.resolve({
        id: ASSET_ID,
        display_name: "Olive Oil",
        assertions: [{ field_path: "expiry_date", value: "2030-05-06", review_state: "accepted" }],
      });
    }
    return Promise.resolve({ items: [], next_cursor: null, total: 0 });
  });
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("ReviewPage SG-304 G2 (duplicate photo)", () => {
  test("shows the existing item by name and date and never its id", async () => {
    serve();
    renderPage();

    expect(await screen.findByText("This photo matches Olive Oil (use by 6 May 2030).")).toBeInTheDocument();
    expect(document.body.textContent).not.toContain(ASSET_ID);
  });

  test("It's another pack sends accept with the new-pack option, and the new item opens", async () => {
    serve();
    api.candidateDecision.mockResolvedValue({ candidate_id: candidate.id, state: "accepted", asset_id: NEW_ASSET_ID, status: "committed", created: true });
    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: "It's another pack" }));

    await waitFor(() =>
      expect(api.candidateDecision).toHaveBeenLastCalledWith("candidate-304", "hh-304", "accept", expect.anything(), { asNewPack: true })
    );
    expect(await screen.findByRole("link", { name: "Open the item" })).toHaveAttribute("href", `/assets/${NEW_ASSET_ID}?household_id=hh-304`);
  });

  test("It's the same pack sends the plain accept, as before", async () => {
    serve();
    api.candidateDecision.mockResolvedValue({ candidate_id: candidate.id, state: "accepted", asset_id: ASSET_ID, status: "duplicate_linked", created: false });
    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: "It's the same pack" }));

    await waitFor(() => expect(api.candidateDecision).toHaveBeenCalledTimes(1));
    expect(api.candidateDecision).toHaveBeenLastCalledWith("candidate-304", "hh-304", "accept", expect.anything());
    expect(api.candidateDecision.mock.calls[0]).toHaveLength(4);
  });

  test("Decide later sends hold", async () => {
    serve();
    api.candidateDecision.mockResolvedValue({ candidate_id: candidate.id, state: "held" });
    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: "Decide later" }));

    await waitFor(() => expect(api.candidateDecision).toHaveBeenCalledTimes(1));
    expect(api.candidateDecision).toHaveBeenLastCalledWith("candidate-304", "hh-304", "hold", undefined);
  });
});
