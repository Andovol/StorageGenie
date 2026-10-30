import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ExpiryEntryForm } from "./ExpiryEntryForm";

const api = vi.hoisted(() => ({ enterManualExpiry: vi.fn(), clearExpiryDate: vi.fn() }));
vi.mock("../api/client", () => api);

type FormAssertion = {
  id: string;
  field_path: string;
  value: unknown;
  source_type: string;
  review_state: string;
  confidence: number | null;
  source_evidence_ids: string[] | null;
  created_at: string | null;
};

function assertion(
  id: string,
  value: unknown,
  review_state: string,
  created_at = "2026-10-01T00:00:00+00:00"
): FormAssertion {
  return {
    id,
    field_path: "plugin:expiry-tracker/expiry_date",
    value,
    source_type: "user",
    review_state,
    confidence: null,
    source_evidence_ids: [],
    created_at,
  };
}

function renderForm(
  activeAssertion: FormAssertion | null,
  categorySlug = "food_beverages",
  hasWindows = true
) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ExpiryEntryForm
        assetId="asset-1"
        householdId="hh"
        evidenceIds={["ev-1"]}
        activeAssertion={activeAssertion}
        categorySlug={categorySlug}
        hasWindows={hasWindows}
      />
    </QueryClientProvider>
  );
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("ExpiryEntryForm", () => {
  test("pre-fills the active accepted date and saves a change with the active token", async () => {
    api.enterManualExpiry.mockResolvedValue({});
    renderForm(assertion("a-active", { expiry_date: "2030-05-06", date_type: "best_before" }, "accepted"));

    expect(screen.getByTestId("expiry-state")).toHaveTextContent("accepted");
    expect(screen.getByLabelText("Date")).toHaveValue("2030-05-06");
    expect(screen.getByLabelText("Date type")).toHaveValue("best_before");
    expect(screen.getByRole("button", { name: "Save date" })).toBeDisabled();

    fireEvent.change(screen.getByLabelText("Date"), { target: { value: "2030-06-06" } });
    fireEvent.click(screen.getByRole("button", { name: "Save date" }));

    await waitFor(() =>
      expect(api.enterManualExpiry).toHaveBeenCalledWith(
        "asset-1",
        "hh",
        {
          expiry_date: "2030-06-06",
          date_type: "best_before",
          source_evidence_ids: ["ev-1"],
        },
        "a-active"
      )
    );
    expect(await screen.findByText("Date saved and re-read from the asset.")).toBeInTheDocument();
  });

  test("a no-op Save writes nothing", () => {
    renderForm(assertion("a-active", { expiry_date: "2030-05-06", date_type: "expiry_date" }, "accepted"));

    const save = screen.getByRole("button", { name: "Save date" });
    expect(save).toBeDisabled();
    fireEvent.click(save);
    expect(api.enterManualExpiry).not.toHaveBeenCalled();
  });

  test("a proposed date is accepted by the user's click", async () => {
    api.enterManualExpiry.mockResolvedValue({});
    renderForm(assertion("a-proposed", { expiry_date: "2030-05-06", date_type: "expiry_date" }, "proposed"));

    const accept = screen.getByRole("button", { name: "Accept date" });
    expect(accept).not.toBeDisabled();
    fireEvent.click(accept);

    await waitFor(() =>
      expect(api.enterManualExpiry).toHaveBeenCalledWith(
        "asset-1",
        "hh",
        expect.objectContaining({ expiry_date: "2030-05-06" }),
        "a-proposed"
      )
    );
  });

  test("Clear sends the active token and empties the date", async () => {
    api.clearExpiryDate.mockResolvedValue({ asset_id: "asset-1", assertion: null });
    renderForm(assertion("a-active", { expiry_date: "2030-05-06", date_type: "expiry_date" }, "accepted"));

    fireEvent.click(screen.getByRole("button", { name: "Clear expiry date" }));

    await waitFor(() =>
      expect(api.clearExpiryDate).toHaveBeenCalledWith("asset-1", "hh", "a-active")
    );
    expect(await screen.findByText("Date cleared.")).toBeInTheDocument();
    expect(screen.getByLabelText("Date")).toHaveValue("");
  });

  test("documents default to Valid until and use date language", () => {
    renderForm(assertion("a-empty", null, "accepted"), "documents_other");

    expect(screen.getByRole("heading", { name: "Manual date entry" })).toBeInTheDocument();
    expect(screen.getByLabelText("Date type")).toHaveValue("valid_until");
    expect(screen.getByRole("option", { name: "Valid until" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Clear expiry date" })).not.toBeInTheDocument();
  });

  test("hides itself for a category without expiry windows", () => {
    const { container } = renderForm(assertion("a-empty", null, "accepted"), "non_perishable", false);
    expect(container).toBeEmptyDOMElement();
  });
});
