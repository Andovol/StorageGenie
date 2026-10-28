import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { OpenedCountdownSection } from "./OpenedCountdownSection";
import type { OpenedCountdownRow } from "../api/types";

const openedRow: OpenedCountdownRow = {
  asset_id: "a1",
  display_name: "Serum",
  category: "cosmetics_personal_care",
  opened_date: "2026-01-31",
  days_open: 15,
  window_months: 12,
  window_source: "category_default",
  days_remaining: 350,
  window_end: "2027-01-31",
};

const unopenedRow: OpenedCountdownRow = {
  asset_id: "a2",
  display_name: "Moisturiser",
  category: "cosmetics_personal_care",
  opened_date: null,
  days_open: null,
  window_months: 12,
  window_source: "category_default",
  days_remaining: null,
  window_end: null,
};

const passedRow: OpenedCountdownRow = {
  asset_id: "a3",
  display_name: "Old cream",
  category: "cosmetics_personal_care",
  opened_date: "2024-01-01",
  days_open: 800,
  window_months: 12,
  window_source: "category_default",
  days_remaining: -123,
  window_end: "2025-01-01",
};

function jsonResponse(body: unknown): Response {
  return { ok: true, json: async () => body } as Response;
}

let rows: OpenedCountdownRow[];
let openedGetCount: number;
let fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
  void input;
  void init;
  return Promise.resolve(jsonResponse({}));
});

beforeEach(() => {
  rows = [openedRow, unopenedRow];
  openedGetCount = 0;
  fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const url = String(input);
    const method = init?.method ?? "GET";
    if (url.includes("/assets/a1/opened/clear") && method === "POST") {
      rows = rows.map((row) =>
        row.asset_id === "a1"
          ? { ...openedRow, opened_date: null, days_open: null, days_remaining: null, window_end: null }
          : row
      );
      return Promise.resolve(
        jsonResponse({
          asset_id: "a1",
          assertion: {
            id: "as2",
            field_path: "opened_date",
            value: null,
            source_type: "user",
            review_state: "accepted",
            confidence: null,
            source_evidence_ids: null,
            created_at: null,
          },
        })
      );
    }
    if (url.includes("/assets/a1/opened") && method === "POST") {
      rows = rows.map((row) =>
        row.asset_id === "a1"
          ? {
              ...openedRow,
              opened_date: "2026-10-01",
              days_open: 23,
              days_remaining: 342,
              window_end: "2027-10-01",
            }
          : row
      );
      return Promise.resolve(
        jsonResponse({
          asset_id: "a1",
          assertion: {
            id: "as3",
            field_path: "opened_date",
            value: "2026-10-01",
            source_type: "user",
            review_state: "accepted",
            confidence: null,
            source_evidence_ids: null,
            created_at: null,
          },
        })
      );
    }
    if (url.includes("/assets/a2/opened") && method === "POST") {
      rows = [
        openedRow,
        {
          ...unopenedRow,
          opened_date: "2026-10-01",
          days_open: 23,
          days_remaining: 342,
          window_end: "2027-10-01",
        },
      ];
      return Promise.resolve(
        jsonResponse({
          asset_id: "a2",
          assertion: {
            id: "as1",
            field_path: "opened_date",
            value: "2026-10-01",
            source_type: "user",
            review_state: "accepted",
            confidence: null,
            source_evidence_ids: null,
            created_at: null,
          },
        })
      );
    }
    if (url.includes("/v1/plugins/expiry-tracker/opened")) {
      openedGetCount += 1;
      return Promise.resolve(
        jsonResponse({ household_id: "hh-1", as_of: "2026-10-24", rows })
      );
    }
    return Promise.resolve(jsonResponse({}));
  });
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

function renderSection() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>
        <OpenedCountdownSection householdId="hh-1" />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("OpenedCountdownSection", () => {
  test("renders the countdown text and the window with its source", async () => {
    renderSection();
    await screen.findByText("Serum");

    expect(screen.getByText("Opened 2026-01-31")).toBeInTheDocument();
    expect(screen.getByText("15 days open")).toBeInTheDocument();
    expect(screen.getByText("350 days left")).toBeInTheDocument();
    expect(screen.getAllByTestId("opened-window").map((node) => node.textContent)).toEqual([
      "12-month default",
      "12-month default",
    ]);
    expect(screen.getByRole("link", { name: "Serum" })).toHaveAttribute(
      "href",
      "/assets/a1?household_id=hh-1"
    );
    expect(fetchMock).toHaveBeenCalled();
  });

  test("saving a date posts it and re-reads the same query", async () => {
    rows = [unopenedRow];
    renderSection();
    const input = await screen.findByLabelText("Opened date for Moisturiser");
    const initialGets = openedGetCount;

    fireEvent.change(input, { target: { value: "2026-10-01" } });
    fireEvent.click(screen.getByRole("button", { name: "Save opened date for Moisturiser" }));

    await waitFor(() => {
      const call = fetchMock.mock.calls.find(
        ([url, init]) =>
          String(url).includes("/v1/plugins/expiry-tracker/assets/a2/opened") &&
          (init as RequestInit | undefined)?.method === "POST"
      );
      expect(call).toBeTruthy();
      expect(String(call?.[0])).toContain("household_id=hh-1");
      expect(JSON.parse(String((call?.[1] as RequestInit).body))).toEqual({
        opened_date: "2026-10-01",
      });
    });
    await waitFor(() => expect(openedGetCount).toBeGreaterThan(initialGets));
    expect(await screen.findByText("Opened 2026-10-01")).toBeInTheDocument();
  });

  test("an opened row shows Edit and Clear, not the no-date form", async () => {
    rows = [openedRow];
    renderSection();
    await screen.findByText("Serum");

    expect(
      screen.getByRole("button", { name: "Edit opened date for Serum" })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Clear opened date for Serum" })
    ).toBeInTheDocument();
    expect(screen.queryByText("No opened date yet")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Opened date for Serum")).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Save opened date for Serum" })
    ).not.toBeInTheDocument();
  });

  test("editing an opened date posts it and re-reads", async () => {
    rows = [openedRow];
    renderSection();
    await screen.findByText("Serum");
    const initialGets = openedGetCount;

    fireEvent.click(screen.getByRole("button", { name: "Edit opened date for Serum" }));
    const input = screen.getByLabelText("Opened date for Serum");
    expect(input).toHaveValue("2026-01-31");
    fireEvent.change(input, { target: { value: "2026-10-01" } });
    fireEvent.click(screen.getByRole("button", { name: "Save opened date for Serum" }));

    await waitFor(() => {
      const call = fetchMock.mock.calls.find(
        ([url, init]) =>
          String(url).includes("/v1/plugins/expiry-tracker/assets/a1/opened") &&
          !String(url).includes("/clear") &&
          (init as RequestInit | undefined)?.method === "POST"
      );
      expect(call).toBeTruthy();
      expect(String(call?.[0])).toContain("household_id=hh-1");
      expect(JSON.parse(String((call?.[1] as RequestInit).body))).toEqual({
        opened_date: "2026-10-01",
      });
    });
    await waitFor(() => expect(openedGetCount).toBeGreaterThan(initialGets));
    expect(await screen.findByText("Opened 2026-10-01")).toBeInTheDocument();
  });

  test("clearing an opened date posts to the clear route and returns the row to the form", async () => {
    rows = [openedRow];
    renderSection();
    await screen.findByText("Serum");
    const initialGets = openedGetCount;

    fireEvent.click(screen.getByRole("button", { name: "Clear opened date for Serum" }));

    await waitFor(() => {
      const call = fetchMock.mock.calls.find(
        ([url, init]) =>
          String(url).includes("/v1/plugins/expiry-tracker/assets/a1/opened/clear") &&
          (init as RequestInit | undefined)?.method === "POST"
      );
      expect(call).toBeTruthy();
      expect(String(call?.[0])).toContain("household_id=hh-1");
      expect(JSON.parse(String((call?.[1] as RequestInit).body))).toEqual({});
    });
    await waitFor(() => expect(openedGetCount).toBeGreaterThan(initialGets));
    expect(await screen.findByText("No opened date yet")).toBeInTheDocument();
    expect(screen.getByLabelText("Opened date for Serum")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Edit opened date for Serum" })
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Clear opened date for Serum" })
    ).not.toBeInTheDocument();
  });

  test("an unopened row shows the form and no Edit or Clear", async () => {
    rows = [unopenedRow];
    renderSection();
    await screen.findByText("Moisturiser");

    expect(screen.getByLabelText("Opened date for Moisturiser")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Save opened date for Moisturiser" })
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Edit opened date for Moisturiser" })
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Clear opened date for Moisturiser" })
    ).not.toBeInTheDocument();
  });

  test("renders the empty state when the household has no cosmetics item", async () => {
    rows = [];
    renderSection();

    expect(await screen.findByText("No cosmetics items to track.")).toBeInTheDocument();
    expect(screen.queryByTestId("opened-window")).not.toBeInTheDocument();
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
  });

  test("says in words when the window has passed", async () => {
    rows = [passedRow];
    renderSection();

    expect(await screen.findByText("Window passed 123 days ago")).toBeInTheDocument();
  });
});
