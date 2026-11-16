import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AssetForm } from "./AssetForm";

// SG-304 G1 (F9): a manual capture whose name matches a live item warns first.
const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  uploadEvidence: vi.fn(),
}));
vi.mock("../api/client", () => api);

type Row = { id: string; name: string; status?: string; expiry: string | null };

afterEach(() => {
  vi.clearAllMocks();
});

function serve(rows: Row[]) {
  api.apiGet.mockImplementation((path: string) => {
    if (path === "/v1/assets") {
      return Promise.resolve({
        items: rows.map((row) => ({ id: row.id, display_name: row.name, status: row.status ?? "ACTIVE" })),
        next_cursor: null,
        total: rows.length,
      });
    }
    const row = rows.find((candidate) => path === `/v1/assets/${candidate.id}`);
    return Promise.resolve({
      id: row?.id ?? "",
      display_name: row?.name ?? "",
      assertions: row?.expiry
        ? [{ field_path: "expiry_date", value: row.expiry, review_state: "accepted" }]
        : [],
    });
  });
}

function renderForm() {
  return render(
    <MemoryRouter>
      <AssetForm householdId="hh-1" onCreated={() => {}} />
    </MemoryRouter>
  );
}

function submit(name: string, quantity?: string) {
  fireEvent.change(screen.getByPlaceholderText("e.g. Hammer"), { target: { value: name } });
  if (quantity !== undefined) {
    fireEvent.change(screen.getByLabelText("Quantity"), { target: { value: quantity } });
  }
  fireEvent.click(screen.getByRole("button", { name: "Add to catalog" }));
}

describe("AssetForm SG-304 G1 (same-name warning)", () => {
  test("a live item with the typed name shows one line with its date and creates nothing yet", async () => {
    serve([{ id: "asset-a", name: "Olive Oil", expiry: "2030-05-06" }]);
    renderForm();

    submit("Olive Oil");

    expect(await screen.findByTestId("same-name-warning")).toHaveTextContent(
      "You already have Olive Oil (use by 6 May 2030)."
    );
    expect(api.apiPost).not.toHaveBeenCalled();
  });

  test("no warning on a different name, a disposed item, or a failed lookup", async () => {
    serve([
      { id: "asset-b", name: "Olive Oil Extra", expiry: null },
      { id: "asset-c", name: "Olive Oil", status: "DISPOSED", expiry: null },
    ]);
    api.apiPost.mockResolvedValue({ id: "asset-new" });
    renderForm();

    submit("Olive Oil");

    await waitFor(() => expect(api.apiPost).toHaveBeenCalledTimes(1));
    expect(screen.queryByTestId("same-name-warning")).not.toBeInTheDocument();
  });

  test("a failed lookup never blocks the create (today's path)", async () => {
    api.apiGet.mockRejectedValue(new Error("lookup down"));
    api.apiPost.mockResolvedValue({ id: "asset-new" });
    renderForm();

    submit("Olive Oil");

    await waitFor(() => expect(api.apiPost).toHaveBeenCalledTimes(1));
    expect(screen.queryByTestId("same-name-warning")).not.toBeInTheDocument();
  });

  test("the match ignores case and surrounding spaces", async () => {
    serve([{ id: "asset-a", name: "Olive Oil", expiry: "2030-05-06" }]);
    renderForm();

    submit("  olive OIL ");

    expect(await screen.findByTestId("same-name-warning")).toHaveTextContent("You already have Olive Oil");
    expect(api.apiPost).not.toHaveBeenCalled();
  });

  test("two same-name packs with distinct dates: one line each with its date and an Open it link", async () => {
    serve([
      { id: "asset-a", name: "Olive Oil", expiry: "2030-05-06" },
      { id: "asset-b", name: "Olive Oil", expiry: "2031-02-03" },
    ]);
    renderForm();

    submit("Olive Oil");

    const warning = await screen.findByTestId("same-name-warning");
    expect(warning).toHaveTextContent("You already have these:");
    const lines = within(warning).getAllByRole("listitem");
    expect(lines).toHaveLength(2);
    expect(lines[0]).toHaveTextContent("Olive Oil (use by 6 May 2030)");
    expect(lines[1]).toHaveTextContent("Olive Oil (use by 3 Feb 2031)");
    expect(within(lines[0]).getByRole("link", { name: "Open it" })).toHaveAttribute(
      "href",
      "/assets/asset-a?household_id=hh-1"
    );
    expect(within(lines[1]).getByRole("link", { name: "Open it" })).toHaveAttribute(
      "href",
      "/assets/asset-b?household_id=hh-1"
    );
    expect(api.apiPost).not.toHaveBeenCalled();
  });

  test("Add another pack creates the item as today, with the typed name and quantity, once", async () => {
    serve([{ id: "asset-a", name: "Olive Oil", expiry: "2030-05-06" }]);
    api.apiPost.mockResolvedValue({ id: "asset-new" });
    renderForm();

    submit("Olive Oil", "3");
    await screen.findByTestId("same-name-warning");
    fireEvent.click(screen.getByRole("button", { name: "Add another pack" }));

    await waitFor(() => expect(api.apiPost).toHaveBeenCalledTimes(1));
    expect(api.apiPost).toHaveBeenCalledWith(
      "/v1/assets",
      expect.objectContaining({ display_name: "Olive Oil", quantity: 3 }),
      { household_id: "hh-1" },
      { "Idempotency-Key": expect.any(String) }
    );
    expect(screen.queryByTestId("same-name-warning")).not.toBeInTheDocument();
  });

  test("Open it creates nothing and keeps the form as typed", async () => {
    serve([{ id: "asset-a", name: "Olive Oil", expiry: "2030-05-06" }]);
    renderForm();

    submit("Olive Oil", "3");
    const open = await screen.findByRole("link", { name: "Open it" });
    expect(open).toHaveAttribute("href", "/assets/asset-a?household_id=hh-1");

    expect(api.apiPost).not.toHaveBeenCalled();
    expect(screen.getByPlaceholderText("e.g. Hammer")).toHaveValue("Olive Oil");
    expect(screen.getByLabelText("Quantity")).toHaveValue(3);
  });

  test("Cancel creates nothing, removes the warning, and keeps the form as typed", async () => {
    serve([{ id: "asset-a", name: "Olive Oil", expiry: "2030-05-06" }]);
    renderForm();

    submit("Olive Oil", "3");
    await screen.findByTestId("same-name-warning");
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(screen.queryByTestId("same-name-warning")).not.toBeInTheDocument();
    expect(api.apiPost).not.toHaveBeenCalled();
    expect(screen.getByPlaceholderText("e.g. Hammer")).toHaveValue("Olive Oil");
    expect(screen.getByLabelText("Quantity")).toHaveValue(3);
  });
});
