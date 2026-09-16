import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ItemInspectorDrawer } from "./ItemInspectorDrawer";
import type { Asset, Assertion } from "../../api/types";

const api = vi.hoisted(() => ({ apiGet: vi.fn(), apiPatch: vi.fn() }));
vi.mock("../../api/client", () => api);

function assertion(
  id: string,
  field_path: string,
  value: unknown,
  review_state = "accepted"
): Assertion {
  return {
    id,
    field_path,
    value,
    source_type: "inferred",
    review_state,
    confidence: 0.82,
    source_evidence_ids: ["ev-1"],
    created_at: null,
  };
}

const baseAsset: Asset = {
  id: "asset-1",
  household_id: "h1",
  display_name: "Cordless Drill",
  asset_type: "Hardware & Tools",
  status: "ACTIVE",
  quantity: 1,
  unit: "pcs",
  condition: "used",
  version: 1,
  created_at: "2026-09-10T00:00:00Z",
  updated_at: null,
  evidence: [
    {
      id: "ev-1",
      sha256: "abc",
      storage_key: "key",
      media_type: "image/jpeg",
      original_filename: "drill.jpg",
      size_bytes: 10,
    },
  ],
  assertions: [assertion("a-color", "primary_colors", ["#1f2937", "#f59e0b"])],
};

const afterPatch: Asset = {
  ...baseAsset,
  version: 2,
  display_name: "Renamed Drill",
  asset_type: "Home & Decor",
};

function renderDrawer(asset: Asset = baseAsset, onClose = vi.fn()) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const result = render(
    <QueryClientProvider client={client}>
      <ItemInspectorDrawer asset={asset} householdId="h1" onClose={onClose} />
    </QueryClientProvider>
  );
  return { ...result, onClose };
}

beforeEach(() => {
  api.apiGet.mockReset();
  api.apiPatch.mockReset();
  api.apiGet.mockResolvedValue(baseAsset);
  api.apiPatch.mockResolvedValue(afterPatch);
});

afterEach(() => {
  vi.clearAllMocks();
});

describe("ItemInspectorDrawer", () => {
  test("opens with the title, category badge and a source photo at full bleed", async () => {
    renderDrawer();
    expect(await screen.findByTestId("inspector-drawer")).toBeInTheDocument();
    expect(screen.getByTestId("drawer-title")).toHaveTextContent("Cordless Drill");
    expect(screen.getByTestId("drawer-category")).toHaveTextContent("Hardware & Tools");
    expect(screen.getByRole("tab", { name: "Source Photo" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByTestId("source-image")).toHaveAttribute(
      "src",
      expect.stringContaining("/v1/evidence/ev-1/file?household_id=h1")
    );
  });

  test("moves focus to the close button on open and back to the invoking element on close", async () => {
    const invoker = document.createElement("button");
    invoker.textContent = "open";
    document.body.appendChild(invoker);
    invoker.focus();
    expect(document.activeElement).toBe(invoker);

    const { onClose } = renderDrawer();
    expect(await screen.findByTestId("inspector-drawer")).toBeInTheDocument();
    await waitFor(() => expect(document.activeElement).toBe(screen.getByRole("button", { name: "Close inspector" })));

    fireEvent.click(screen.getByRole("button", { name: "Close inspector" }));
    expect(onClose).toHaveBeenCalledTimes(1);
    invoker.remove();
  });

  test("Esc closes the drawer", async () => {
    const { onClose } = renderDrawer();
    await screen.findByTestId("inspector-drawer");
    fireEvent.keyDown(document, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  test("the cutout tab states cutouts are not available, with no spinner", async () => {
    renderDrawer();
    await screen.findByTestId("inspector-drawer");
    fireEvent.click(screen.getByRole("tab", { name: "Isolated Cutout" }));

    const honest = screen.getByTestId("cutout-honest-state");
    expect(honest).toHaveTextContent(/cutouts arrive with the AI stages/i);
    expect(screen.queryByTestId("source-image")).not.toBeInTheDocument();
  });

  test("the scene tab states scene rendering is not available and draws no bounding box", async () => {
    renderDrawer();
    await screen.findByTestId("inspector-drawer");
    fireEvent.click(screen.getByRole("tab", { name: "Scene / Context" }));

    expect(screen.getByTestId("scene-honest-state")).toHaveTextContent(/scene rendering arrives with the AI stages/i);
    expect(screen.getByText(/bounding-box overlay omitted/i)).toBeInTheDocument();
  });

  test("Title + Category save PATCHes display_name/asset_type with If-Match", async () => {
    renderDrawer();
    await screen.findByTestId("inspector-drawer");

    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Renamed Drill" } });
    fireEvent.change(screen.getByLabelText("Category"), { target: { value: "Home & Decor" } });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));

    await waitFor(() =>
      expect(api.apiPatch).toHaveBeenCalledWith(
        "/v1/assets/asset-1",
        expect.objectContaining({ display_name: "Renamed Drill", asset_type: "Home & Decor" }),
        { household_id: "h1" },
        { "If-Match": "1" }
      )
    );
  });

  test("a custom (passthrough) category is sent unchanged", async () => {
    renderDrawer();
    await screen.findByTestId("inspector-drawer");

    fireEvent.change(screen.getByLabelText("Category"), { target: { value: "Vintage Linens" } });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));

    await waitFor(() =>
      expect(api.apiPatch).toHaveBeenCalledWith(
        "/v1/assets/asset-1",
        expect.objectContaining({ asset_type: "Vintage Linens" }),
        expect.anything(),
        expect.anything()
      )
    );
  });

  test("observed colors and description are read-only rows, with an honest absent state", async () => {
    renderDrawer();
    await screen.findByTestId("inspector-drawer");

    expect(screen.getByTestId("drawer-colors")).toHaveTextContent("#1f2937, #f59e0b");
    expect(screen.getByTestId("drawer-description")).toHaveTextContent(/no functional description assertion/i);
    expect(screen.queryByLabelText(/colors/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/description/i)).not.toBeInTheDocument();
  });

  test("the AI buttons show the honest notice and send no request", async () => {
    renderDrawer();
    await screen.findByTestId("inspector-drawer");

    const before = api.apiGet.mock.calls.length + api.apiPatch.mock.calls.length;
    fireEvent.click(screen.getByRole("button", { name: /re-isolate asset/i }));
    fireEvent.click(screen.getByRole("button", { name: /generate context scene/i }));

    expect(screen.getByTestId("ai-notice")).toHaveTextContent(
      "scene rendering lands with the AI stages — nothing was sent anywhere"
    );
    expect(api.apiGet.mock.calls.length + api.apiPatch.mock.calls.length).toBe(before);
  });

  test("the raw panel expands with the asset + assertions JSON, coordinates/confidence as data", async () => {
    renderDrawer();
    await screen.findByTestId("inspector-drawer");
    expect(screen.queryByTestId("raw-json")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /raw data/i }));
    const raw = screen.getByTestId("raw-json");
    expect(raw.textContent).toContain("asset-1");
    expect(raw.textContent).toContain("primary_colors");
    expect(raw.textContent).toContain("0.82");
  });

  test("an asset with no evidence shows the honest empty source state", async () => {
    renderDrawer({ ...baseAsset, evidence: [] });
    await screen.findByTestId("inspector-drawer");
    expect(screen.getByTestId("source-empty")).toHaveTextContent(/no source photo is attached/i);
  });

  test("a null display_name shows the Untitled asset fallback and an empty editable title", async () => {
    const nameless: Asset = { ...baseAsset, display_name: null, evidence: [] };
    api.apiGet.mockResolvedValue(nameless);
    renderDrawer(nameless);
    await screen.findByTestId("inspector-drawer");
    expect(screen.getByTestId("drawer-title")).toHaveTextContent("Untitled asset");
    expect(screen.getByLabelText("Title")).toHaveValue("");
  });

  test("a successful save invalidates the assets and asset query keys", async () => {
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const spy = vi.spyOn(client, "invalidateQueries");
    render(
      <QueryClientProvider client={client}>
        <ItemInspectorDrawer asset={baseAsset} householdId="h1" onClose={vi.fn()} />
      </QueryClientProvider>
    );
    await screen.findByTestId("inspector-drawer");

    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "Renamed Drill" } });
    fireEvent.click(screen.getByRole("button", { name: "Save changes" }));

    await waitFor(() => expect(spy).toHaveBeenCalledWith({ queryKey: ["assets"] }));
    expect(spy).toHaveBeenCalledWith({ queryKey: ["asset", "asset-1"] });
  });
});
