import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AssetForm } from "./components/AssetForm";

// SG-325 P10: every button in the same-name warning and the preview remove
// carry the theme's control treatment (sg-paper-control, 13px or more), light
// and dark — never browser-default grey or 11px.
const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  uploadEvidence: vi.fn(),
}));
vi.mock("./api/client", () => api);

afterEach(() => {
  vi.clearAllMocks();
});

function serveSamePack() {
  api.apiGet.mockImplementation((path: string) => {
    if (path === "/v1/assets") {
      return Promise.resolve({
        items: [{ id: "asset-a", display_name: "Olive Oil", status: "ACTIVE" }],
        next_cursor: null,
        total: 1,
      });
    }
    return Promise.resolve({
      id: "asset-a",
      display_name: "Olive Oil",
      assertions: [{ field_path: "expiry_date", value: "2030-05-06", review_state: "accepted" }],
    });
  });
}

function imageFile(name = "shot.png") {
  return new File([new Uint8Array([0x89, 0x50, 0x4e, 0x47])], name, { type: "image/png" });
}

function themed(button: HTMLElement) {
  expect(button).toHaveClass("sg-paper-control");
  expect(Number.parseFloat(button.style.fontSize)).toBeGreaterThanOrEqual(13);
}

describe("SG-325 P10 warning and preview controls", () => {
  test("the warning's buttons and the preview remove use the themed control style at 13px or more", async () => {
    serveSamePack();
    render(
      <MemoryRouter>
        <AssetForm householdId="hh-1" onCreated={() => {}} />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByPlaceholderText("e.g. Hammer"), { target: { value: "Olive Oil" } });
    fireEvent.click(screen.getByRole("button", { name: "Create asset" }));
    expect(await screen.findByTestId("same-name-warning")).toBeInTheDocument();

    themed(screen.getByRole("button", { name: "Add another pack" }));
    themed(screen.getByRole("button", { name: "Cancel" }));

    fireEvent.paste(screen.getByPlaceholderText("e.g. Hammer"), {
      clipboardData: { files: [imageFile("preview.png")] },
    });
    themed(await screen.findByRole("button", { name: "remove" }));
  });
});
