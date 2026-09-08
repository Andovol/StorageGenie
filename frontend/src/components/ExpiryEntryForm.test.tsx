import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ExpiryEntryForm } from "./ExpiryEntryForm";

const api = vi.hoisted(() => ({ apiGet: vi.fn(), enterManualExpiry: vi.fn() }));
vi.mock("../api/client", () => api);
const before = { id: "asset-loaded-expiry", assertions: [{ id: "assertion-before", field_path: "plugin:expiry_tracker.expiry_date", value: null, source_type: "plugin", review_state: "needs_evidence", confidence: null, source_evidence_ids: [], created_at: null }] };
const after = { ...before, assertions: [{ ...before.assertions[0], id: "assertion-after", value: { expiry_date: "2030-05-06", date_type: "best_before" }, source_type: "user", review_state: "accepted" }] };

afterEach(() => { vi.clearAllMocks(); });

describe("ExpiryEntryForm", () => {
  test("posts selected date type and re-reads resolved state", async () => {
    api.apiGet.mockResolvedValueOnce(before).mockResolvedValueOnce(after);
    api.enterManualExpiry.mockResolvedValue({ assertion: after.assertions[0] });
    render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><ExpiryEntryForm assetId="asset-loaded-expiry" householdId="household-loaded" evidenceIds={["evidence-loaded"]} /></QueryClientProvider>);
    expect(await screen.findByTestId("expiry-state")).toHaveTextContent("needs_evidence");
    fireEvent.change(screen.getByLabelText("Date"), { target: { value: "2030-05-06" } });
    fireEvent.change(screen.getByLabelText("Date type"), { target: { value: "best_before" } });
    fireEvent.click(screen.getByRole("button", { name: "Save expiry" }));
    await waitFor(() => expect(api.enterManualExpiry).toHaveBeenCalledWith("asset-loaded-expiry", "household-loaded", { expiry_date: "2030-05-06", date_type: "best_before", source_evidence_ids: ["evidence-loaded"] }));
    await waitFor(() => expect(screen.getByTestId("expiry-state")).toHaveTextContent("accepted"));
  });

  test("wrong read-back remains visibly unresolved", async () => {
    api.apiGet.mockResolvedValue(before);
    render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><ExpiryEntryForm assetId="asset-loaded-expiry" householdId="household-loaded" /></QueryClientProvider>);
    await waitFor(() => expect(() => expect(screen.getByTestId("expiry-state")).toHaveTextContent("accepted")).toThrow());
  });
});
