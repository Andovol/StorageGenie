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
});
