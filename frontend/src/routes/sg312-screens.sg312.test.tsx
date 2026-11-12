import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { InboxPage } from "./InboxPage";
import { ExpiryPage } from "./ExpiryPage";
import { AssetDetailPage, EnrichButton } from "./AssetDetailPage";
import { JobCard } from "../components/JobCard";
import { HouseholdProvider } from "../hooks/HouseholdContext";
import type { ExpiryStatusResponse, ReminderListResponse } from "../api/types";

const household = { id: "hh-312", name: "SG-312 home", created_at: "2026-01-01" };

const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPatch: vi.fn(),
  apiPost: vi.fn(),
  uploadEvidence: vi.fn(),
  enterManualExpiry: vi.fn(),
  clearExpiryDate: vi.fn(),
  classifyAsset: vi.fn(),
  fetchLocations: vi.fn(),
  assignAssetLocation: vi.fn(),
  unassignAssetLocation: vi.fn(),
  fetchRelations: vi.fn(),
  createRelation: vi.fn(),
  deleteRelation: vi.fn(),
  fetchHouseholdAssets: vi.fn(),
}));
vi.mock("../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../api/client")>()),
  ...api,
}));
vi.mock("../hooks/useAssets", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../hooks/useAssets")>()),
  useHouseholds: () => ({ data: [household] }),
}));

const taxonomy = {
  plugins: [
    {
      plugin_id: "expiry-tracker",
      version: "1.0.0",
      categories: [
        { id: "food_beverages", name: "Food & beverages", active: true, notification: "tiered-30-7-1", opened_date_tracking: false, chat: "category" },
        { id: "non_perishable", name: "Non-perishable", active: true, notification: "none", opened_date_tracking: false, chat: "none" },
      ],
      date_types: ["expiry_date"],
      units: ["ml"],
    },
  ],
};

function jsonResponse(body: unknown): Response {
  return { ok: true, json: async () => body } as Response;
}

function withClient(node: React.ReactNode) {
  return (
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <HouseholdProvider>
        <MemoryRouter initialEntries={[`/assets/asset-312?household_id=${household.id}`]}>
          <Routes>
            <Route path="/assets/:id" element={node} />
            <Route path="*" element={node} />
          </Routes>
        </MemoryRouter>
      </HouseholdProvider>
    </QueryClientProvider>
  );
}

afterEach(() => {
  vi.clearAllMocks();
  vi.unstubAllGlobals();
});

describe("SG-312 Inbox in plain words (I3)", () => {
  const job = { id: "job-312", job_type: "import", state: "AWAITING_REVIEW", household_id: household.id, created_at: new Date(2020, 2, 5, 14, 42).toISOString(), updated_at: null };

  test("the job card shows the date as 5 Mar, 14:42, never the ISO string", async () => {
    api.apiGet.mockImplementation((path: string) => (path === "/v1/jobs" ? Promise.resolve({ items: [job], next_cursor: null, total: 1 }) : Promise.resolve({ items: [], next_cursor: null, total: 0 })));
    render(withClient(<InboxPage />));
    expect(await screen.findByText("5 Mar, 14:42")).toBeInTheDocument();
    expect(screen.queryByText(job.created_at)).toBeNull();
  });

  test("the selected job lists its steps as Checking the file, Saving; no raw step name shows", async () => {
    const detail = {
      ...job,
      steps: [
        { id: "s1", step_name: "EXTRACTING_DETERMINISTIC_SIGNALS", state: "COMPLETED", attempts: 1, input: null, output: null, error: null },
        { id: "s2", step_name: "COMMITTING", state: "RUNNING", attempts: 1, input: null, output: null, error: null },
      ],
      progress: { completed: 1, total: 2, failed: 0, pending: 1 },
      errors: [],
    };
    api.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/jobs") return Promise.resolve({ items: [job], next_cursor: null, total: 1 });
      if (path === `/v1/imports/${job.id}`) return Promise.resolve(detail);
      return Promise.resolve({ items: [], next_cursor: null, total: 0 });
    });
    render(withClient(<InboxPage />));
    fireEvent.click(await screen.findByText("Import job"));
    expect(await screen.findByText("Checking the file")).toBeInTheDocument();
    expect(screen.getByText("Saving")).toBeInTheDocument();
    expect(screen.queryByText("COMMITTING")).toBeNull();
    expect(screen.queryByText("EXTRACTING_DETERMINISTIC_SIGNALS")).toBeNull();
  });

  test("review rows name the item when a read gives the name; no bare item or candidate word", async () => {
    const assetTask = { id: "task-312-a", task_type: "expiry.manual_entry", priority: "high", subject_ref: "asset-312", subject_kind: "asset", data_required: true, proposed_change: null, status: "open", household_id: household.id, created_at: null, updated_at: null };
    const candidateTask = { id: "task-312-c", task_type: "identifier_collision", priority: "high", subject_ref: "candidate-312", subject_kind: "candidate", data_required: false, proposed_change: null, status: "open", household_id: household.id, created_at: null, updated_at: null };
    api.apiGet.mockImplementation((path: string) => (path === "/v1/jobs" ? Promise.resolve({ items: [], next_cursor: null, total: 0 }) : Promise.resolve({ items: [assetTask, candidateTask], next_cursor: null, total: 2 })));
    api.fetchHouseholdAssets.mockResolvedValue({ items: [{ id: "asset-312", display_name: "Oat milk" }], next_cursor: null, total: 1 });
    render(withClient(<InboxPage />));
    expect(await screen.findByText("Oat milk")).toBeInTheDocument();
    expect(screen.getByText("Unnamed item")).toBeInTheDocument();
    expect(screen.queryByText("item")).toBeNull();
    expect(screen.queryByText("candidate")).toBeNull();
  });
});

describe("SG-312 JobCard date (I3)", () => {
  test("renders the formatted date from created_at", () => {
    render(<JobCard job={{ id: "j", job_type: "import", state: "COMPLETED", household_id: "h", created_at: new Date(2020, 2, 5, 14, 42).toISOString(), updated_at: null }} selected={false} onSelect={vi.fn()} />);
    expect(screen.getByText("5 Mar, 14:42")).toBeInTheDocument();
  });
});

describe("SG-312 Expiry tier words (I6)", () => {
  const row = (id: string, tier: string | null) => ({ asset_id: id, display_name: `Item ${id}`, days_remaining: 2, tier, bucket: "this-week", category: "food_beverages", expiry_date: "2026-11-14", date_type: "expiry_date", as_of_day: "2026-11-12" });
  const status: ExpiryStatusResponse = {
    household_id: household.id,
    as_of: "2026-11-12",
    category: null,
    rows: [row("a", "critical"), row("b", "urgent"), row("c", null)] as never,
    summary: { by_tier: {}, by_bucket: {}, unresolved: 0, total: 3, dateless: 0 },
    unresolved_rows: [],
  };
  const reminders: ReminderListResponse = { household_id: household.id, unread_count: 0, items: [] };
  const summary = {
    household_id: household.id,
    as_of_date: "2026-11-12",
    generated_at: "2026-11-12T00:00:00+00:00",
    assets: { total: 3, active: 3, by_status: {} },
    categories: { taxonomy: [], counts: {}, uncategorized: 0 },
    expiry: {},
    waste: { expired_untouched: 0 },
    adherence: { suggestions: {}, review_tasks: {} },
    stats: [],
  };

  beforeEach(() => {
    api.apiGet.mockImplementation((path: string) => (path.includes("/v1/taxonomy") ? Promise.resolve(taxonomy) : Promise.resolve({ items: [], next_cursor: null, total: 0 })));
    vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/v1/reminders")) return Promise.resolve(jsonResponse(reminders));
      if (url.includes("/v1/plugins/expiry-tracker/opened")) return Promise.resolve(jsonResponse({ household_id: household.id, as_of: "2026-11-12", rows: [] }));
      if (url.includes("/v1/plugins/expiry-tracker/status")) return Promise.resolve(jsonResponse(status));
      if (url.includes("/v1/analytics/summary")) return Promise.resolve(jsonResponse(summary));
      return Promise.resolve(jsonResponse({}));
    }));
  });

  test("critical reads Use first, urgent reads Use soon, and a row with no tier shows no pill", async () => {
    render(withClient(<ExpiryPage />));
    expect(await screen.findByText("Use first")).toBeInTheDocument();
    expect(screen.getByText("Use soon")).toBeInTheDocument();
    expect(screen.queryByText("Critical")).toBeNull();
    expect(screen.queryByText("Urgent")).toBeNull();
    expect(screen.queryByText("No tier")).toBeNull();
    expect(screen.getAllByTestId("tier-pill")).toHaveLength(2);
  });

  test("the tier word sits beside the date, not pinned to the far edge", async () => {
    render(withClient(<ExpiryPage />));
    const pill = await screen.findByText("Use first");
    expect(pill.style.marginLeft).not.toBe("auto");
  });
});

describe("SG-312 asset page and Enrich wording (I1, I5)", () => {
  const evidence = [{ id: "ev-1", sha256: "sha", storage_key: "key", original_filename: "photo.jpg" }];
  const assertion = (id: string, field_path: string, value: unknown, review_state: string) => ({ id, field_path, value, source_type: "user", review_state, confidence: null, source_evidence_ids: [], created_at: "2026-10-01T00:00:00+00:00" });
  const asset = {
    id: "asset-312",
    household_id: household.id,
    display_name: "Oat milk",
    asset_type: "product",
    status: "ACTIVE",
    quantity: 500,
    unit: "ml",
    condition: null,
    version: 1,
    created_at: "2026-09-14T00:00:00+00:00",
    updated_at: null,
    evidence,
    audit_events: [],
    assertions: [
      assertion("a-name", "display_name", "Oat milk", "accepted"),
      assertion("a-class", "plugin:expiry-tracker/classification", { category: "food_beverages", label: "food_beverages", profile: { notification_tier: "critical", notification_days: 1, tier_defaults: { critical: 1, urgent: 7 }, opened_date_tracking: false, disposal_guidance: false } }, "accepted"),
      assertion("a-exp", "plugin:expiry-tracker/expiry_date", { status: "unknown" }, "needs_evidence"),
    ],
  };

  beforeEach(() => {
    api.apiGet.mockImplementation((path: string) => (path.includes("/v1/taxonomy") ? Promise.resolve(taxonomy) : Promise.resolve(asset)));
    api.fetchLocations.mockRejectedValue(new Error("locations disabled"));
    api.fetchRelations.mockRejectedValue(new Error("relations disabled"));
  });

  test("the header reads 500 ml left, not qty", async () => {
    render(withClient(<AssetDetailPage />));
    expect(await screen.findByText("Live · 500 ml left")).toBeInTheDocument();
    expect(screen.queryByText(/qty/)).toBeNull();
  });

  test("the Enrich line reads Enrich costs up to $0.05 a press, with no per-press or last-spend wording", async () => {
    render(withClient(<AssetDetailPage />));
    expect(await screen.findByText("Enrich costs up to $0.05 a press")).toBeInTheDocument();
    expect(screen.queryByText(/per-press/)).toBeNull();
    expect(screen.queryByText(/Last measured spend/)).toBeNull();
  });

  test("EnrichButton alone renders the plain line", () => {
    render(<EnrichButton lastSpendUsd={null} />);
    expect(screen.getByText("Enrich costs up to $0.05 a press")).toBeInTheDocument();
  });

  test("the Manual expiry card reads Needs a date, not the evidence-state sentence, and sits on paper", async () => {
    render(withClient(<AssetDetailPage />));
    const card = await screen.findByLabelText("Manual expiry entry");
    expect(within(card).getByText("Needs a date")).toBeInTheDocument();
    expect(screen.queryByText(/evidence state/)).toBeNull();
    expect(card.className).not.toContain("bg-card");
    expect(card.getAttribute("style") ?? "").toContain("var(--paper)");
  });
});
