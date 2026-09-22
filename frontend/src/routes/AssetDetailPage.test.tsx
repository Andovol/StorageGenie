import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AssetDetailPage, EnrichButton, enrichCapRefusal, ENRICH_PER_PRESS_CAP_USD } from "./AssetDetailPage";

const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPatch: vi.fn(),
  apiPost: vi.fn(),
  uploadEvidence: vi.fn(),
  enterManualExpiry: vi.fn(),
}));
vi.mock("../api/client", () => api);

const evidence = [
  { id: "ev-1", sha256: "sha", storage_key: "key", original_filename: "photo.jpg" },
];

function assertion(id: string, field_path: string, value: unknown, review_state: string) {
  return { id, field_path, value, source_type: "user", review_state, confidence: null, source_evidence_ids: [], created_at: null };
}

const before = {
  id: "asset-1",
  household_id: "hh",
  display_name: "Milk",
  asset_type: "product",
  status: "ACTIVE",
  quantity: 2,
  unit: "piece",
  condition: null,
  version: 1,
  created_at: "2026-09-14T00:00:00+00:00",
  updated_at: null,
  evidence,
  assertions: [assertion("a-name", "display_name", "Milk", "accepted"), assertion("a-qty-old", "quantity", 2, "accepted")],
  audit_events: [],
};

const after = {
  ...before,
  version: 2,
  quantity: 3,
  assertions: [
    assertion("a-name", "display_name", "Milk", "accepted"),
    assertion("a-qty-old", "quantity", 2, "superseded"),
    assertion("a-qty-new", "quantity", 3, "accepted"),
  ],
  audit_events: [{ id: "ae-1", action: "asset.update", actor: "api", timestamp: "2026-09-14T00:00:01+00:00", before: {}, after: { quantity: 3 } }],
};

const needsEvidence = {
  ...before,
  assertions: [
    assertion("a-name", "display_name", "Milk", "accepted"),
    assertion("a-exp", "plugin:expiry-tracker/expiry_date", { status: "unknown" }, "needs_evidence"),
  ],
};

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={["/assets/asset-1?household_id=hh"]}>
        <Routes>
          <Route path="/assets/:id" element={<AssetDetailPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("AssetDetailPage", () => {
  test("editing quantity patches via PATCH and shows the superseded prior value in history", async () => {
    api.apiGet.mockResolvedValueOnce(before).mockResolvedValueOnce(after);
    api.apiPatch.mockResolvedValue(after);
    renderPage();

    fireEvent.click(await screen.findByRole("button", { name: "Edit" }));
    fireEvent.change(await screen.findByLabelText("Quantity"), { target: { value: "3" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() =>
      expect(api.apiPatch).toHaveBeenCalledWith(
        "/v1/assets/asset-1",
        expect.objectContaining({ display_name: "Milk", quantity: 3 }),
        { household_id: "hh" },
        { "If-Match": "1" }
      )
    );
    expect(await screen.findByText("superseded")).toBeInTheDocument();
    expect(await screen.findByText("asset.update")).toBeInTheDocument();
  });

  test("a needs_evidence asset offers hand entry beside its detail and refuses an empty date", async () => {
    api.apiGet.mockResolvedValue(needsEvidence);
    api.enterManualExpiry.mockResolvedValue({ assertion: null, resolved_review_task_ids: [] });
    renderPage();

    expect(await screen.findByText("Manual expiry entry")).toBeInTheDocument();
    const save = screen.getByRole("button", { name: "Save expiry" });
    expect(save).toBeDisabled();

    fireEvent.change(screen.getByLabelText("Date"), { target: { value: "2030-05-06" } });
    await waitFor(() => expect(save).not.toBeDisabled());
    fireEvent.click(save);

    await waitFor(() =>
      expect(api.enterManualExpiry).toHaveBeenCalledWith(
        "asset-1",
        "hh",
        expect.objectContaining({ expiry_date: "2030-05-06", source_evidence_ids: ["ev-1"] })
      )
    );
  });
});

describe("EnrichButton per-press cap (SG-082)", () => {
  test("the page renders the Enrich button with the last measured spend and cap", async () => {
    api.apiGet.mockResolvedValue(before);
    renderPage();

    expect(await screen.findByRole("button", { name: "Enrich" })).toBeInTheDocument();
    expect(screen.getByText(`Last measured spend: $0.00 · per-press cap $${ENRICH_PER_PRESS_CAP_USD.toFixed(2)}`)).toBeInTheDocument();
  });

  test("cap helper refuses above the cap with a named reason (seen-to-fail) and allows below", () => {
    expect(enrichCapRefusal(0.01)).toBeNull();
    expect(enrichCapRefusal(0.06)).toBe(
      "per_press_cap_exceeded: last press cost $0.060000 exceeds cap $0.05"
    );
  });

  test("a press above the cap is refused and never runs; below the cap it runs", () => {
    const run = vi.fn();
    const { rerender } = render(<EnrichButton lastSpendUsd={0.06} onRun={run} />);

    expect(screen.getByText("Last measured spend: $0.060000 · per-press cap $0.05")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Enrich" }));
    expect(run).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent(
      "per_press_cap_exceeded: last press cost $0.060000 exceeds cap $0.05"
    );

    rerender(<EnrichButton lastSpendUsd={0.01} onRun={run} />);
    fireEvent.click(screen.getByRole("button", { name: "Enrich" }));
    expect(run).toHaveBeenCalledTimes(1);
  });
});
