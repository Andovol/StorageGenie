import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { AssetForm } from "./AssetForm";

const api = vi.hoisted(() => ({
  apiPost: vi.fn(),
  uploadEvidence: vi.fn(),
}));
vi.mock("../api/client", () => api);

afterEach(() => {
  vi.clearAllMocks();
});

function imageFile(name = "pasted.png") {
  return new File([new Uint8Array([0x89, 0x50, 0x4e, 0x47])], name, { type: "image/png" });
}

describe("AssetForm", () => {
  test("a paste carrying an image file stages it with name and size, and remove deletes it", async () => {
    render(<AssetForm householdId="hh-1" onCreated={() => {}} />);

    fireEvent.paste(screen.getByPlaceholderText("e.g. Hammer"), {
      clipboardData: { files: [imageFile("pasted.png")] },
    });

    expect(await screen.findByText(/pasted\.png/)).toBeInTheDocument();
    expect(screen.getByText(/KB/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "remove" }));
    await waitFor(() => expect(screen.queryByText(/pasted\.png/)).not.toBeInTheDocument());
  });

  test("a text-only paste stages nothing and disturbs no existing entry", async () => {
    render(<AssetForm householdId="hh-1" onCreated={() => {}} />);

    fireEvent.paste(screen.getByPlaceholderText("e.g. Hammer"), {
      clipboardData: {
        files: [],
        items: [{ kind: "string", getAsFile: () => null }],
        getData: () => "some text",
      },
    });
    expect(screen.queryByText(/KB/)).not.toBeInTheDocument();

    fireEvent.paste(screen.getByPlaceholderText("e.g. Hammer"), {
      clipboardData: { files: [imageFile("kept.png")] },
    });
    expect(await screen.findByText(/kept\.png/)).toBeInTheDocument();
  });

  test("the camera input carries capture=environment and an image-only accept", () => {
    render(<AssetForm householdId="hh-1" onCreated={() => {}} />);

    const camera = screen.getByLabelText("Take a photo");
    expect(camera).toHaveAttribute("type", "file");
    expect(camera).toHaveAttribute("capture", "environment");
    expect(camera).toHaveAttribute("accept", "image/*");
    expect(camera).not.toHaveAttribute("multiple");
  });

  test("submitting with a staged file posts display_name and evidence_ids", async () => {
    api.uploadEvidence.mockResolvedValue({
      id: "ev-1",
      sha256: "sha",
      storage_key: "key",
      size_bytes: 4,
    });
    api.apiPost.mockResolvedValue({ id: "asset-1" });
    const onCreated = vi.fn();

    render(<AssetForm householdId="hh-1" onCreated={onCreated} />);

    fireEvent.paste(screen.getByPlaceholderText("e.g. Hammer"), {
      clipboardData: { files: [imageFile("shot.png")] },
    });
    expect(await screen.findByText(/shot\.png/)).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText("e.g. Hammer"), { target: { value: "Drill" } });
    fireEvent.click(screen.getByRole("button", { name: "Create asset" }));

    await waitFor(() =>
      expect(api.apiPost).toHaveBeenCalledWith(
        "/v1/assets",
        expect.objectContaining({ display_name: "Drill", evidence_ids: ["ev-1"] }),
        { household_id: "hh-1" },
        { "Idempotency-Key": expect.any(String) }
      )
    );
    expect(onCreated).toHaveBeenCalledWith("asset-1");
  });

  test("the name field reads optional and explains the filename fallback", () => {
    render(<AssetForm householdId="hh-1" onCreated={() => {}} />);

    expect(screen.getByText("Display name (optional)")).toBeInTheDocument();
    expect(screen.getByText(/we use the photo's filename/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText("e.g. Hammer")).not.toBeRequired();
  });

  test("a nameless capture with a photo posts no display_name key", async () => {
    api.uploadEvidence.mockResolvedValue({
      id: "ev-2",
      sha256: "sha",
      storage_key: "key",
      size_bytes: 4,
    });
    api.apiPost.mockResolvedValue({ id: "asset-2" });
    const onCreated = vi.fn();

    render(<AssetForm householdId="hh-1" onCreated={onCreated} />);

    fireEvent.paste(screen.getByPlaceholderText("e.g. Hammer"), {
      clipboardData: { files: [imageFile("nameless.png")] },
    });
    expect(await screen.findByText(/nameless\.png/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Create asset" }));

    await waitFor(() => expect(api.apiPost).toHaveBeenCalledTimes(1));
    const payload = api.apiPost.mock.calls[0][1] as Record<string, unknown>;
    expect(payload).not.toHaveProperty("display_name");
    expect(payload).toMatchObject({ asset_type: "unknown", evidence_ids: ["ev-2"] });
    expect(onCreated).toHaveBeenCalledWith("asset-2");
  });

  test("a nameless photoless submit is refused with a named error and sends nothing", async () => {
    render(<AssetForm householdId="hh-1" onCreated={() => {}} />);

    fireEvent.click(screen.getByRole("button", { name: "Create asset" }));

    expect(await screen.findByText("Add a photo or a display name")).toBeInTheDocument();
    expect(api.uploadEvidence).not.toHaveBeenCalled();
    expect(api.apiPost).not.toHaveBeenCalled();
  });

  test("the asset-type select carries the themed control treatment (SG-105 G2)", () => {
    render(<AssetForm householdId="hh-1" onCreated={() => {}} />);

    const select = screen.getByLabelText("Asset type");
    expect(select).toHaveClass("bg-background", "text-foreground", "border-border");
  });

  test("the file pickers are real file inputs hidden behind themed labels (SG-105 G2)", () => {
    render(<AssetForm householdId="hh-1" onCreated={() => {}} />);

    const choose = screen.getByLabelText("Choose files");
    expect(choose).toHaveAttribute("type", "file");
    expect(choose).toHaveAttribute("multiple");
    expect(choose).toHaveAttribute("accept", "image/*,.pdf");
    expect(choose.style.position).toBe("absolute");
    expect(choose.closest("label")).toHaveClass("bg-background", "text-foreground", "border-border");

    const camera = screen.getByLabelText("Take a photo");
    expect(camera).toHaveAttribute("type", "file");
    expect(camera).toHaveAttribute("capture", "environment");
    expect(camera.style.position).toBe("absolute");
    expect(camera.closest("label")).toHaveClass("bg-background", "text-foreground", "border-border");
  });
});
