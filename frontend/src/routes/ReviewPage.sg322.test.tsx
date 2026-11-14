import { afterEach, describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReviewPage } from "./ReviewPage";

// SG-322 G2: the page is fed the shapes GET /v1/candidates/{id} returns (keys as
// in backend/app/api/v1/candidates.py get_candidate), not a candidate the API
// never sends. Case 1: an open duplicate (no asset_id). Case 3: the same-pack read.
const ASSET_ID = "asset-olive-322";
const openDuplicate = {
  id: "candidate-322",
  state: "proposed",
  job_id: "job-322",
  fields: { display_name: "Olive Oil" },
  dedup_matches: [{ type: "duplicate_of_asset", asset_id: ASSET_ID }],
  review_task_ids: [],
  blocking_review_task_ids: [],
  evidence_ids: ["evidence-322"],
  asset_id: null,
  web_alternates: [],
  merged_into: null,
};
const samePackRead = { ...openDuplicate, state: "accepted", asset_id: ASSET_ID };
const api = vi.hoisted(() => ({ apiGet: vi.fn(), candidateDecision: vi.fn(), candidateSplit: vi.fn(), classifyAsset: vi.fn() }));
vi.mock("../api/client", () => api);

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={[`/review/${openDuplicate.id}?household_id=hh-322`]}>
        <Routes>
          <Route path="/review/:candidateId" element={<ReviewPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

function serve(read: object) {
  api.apiGet.mockImplementation((path: string) => {
    if (path.startsWith("/v1/candidates/")) return Promise.resolve(read);
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

describe("ReviewPage SG-322 (open duplicate reads with no asset_id)", () => {
  test("an open duplicate read shows the three choices and not In your catalog", async () => {
    serve(openDuplicate);
    renderPage();

    expect(await screen.findByText("This photo matches Olive Oil (use by 6 May 2030).")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "It's the same pack" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "It's another pack" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Decide later" })).toBeInTheDocument();
    expect(screen.queryByText("In your catalog")).not.toBeInTheDocument();
  });

  test("a same-pack read (asset_id = the existing item) shows In your catalog", async () => {
    serve(samePackRead);
    renderPage();

    expect(await screen.findByText("In your catalog")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open item" })).toHaveAttribute("href", expect.stringContaining(`/assets/${ASSET_ID}`));
    expect(screen.queryByRole("button", { name: "It's the same pack" })).not.toBeInTheDocument();
  });
});
