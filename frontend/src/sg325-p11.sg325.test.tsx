import { describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { HouseholdProvider } from "./hooks/HouseholdContext";
import { CapturePage } from "./routes/CapturePage";
import { AssetForm } from "./components/AssetForm";

// SG-325 P11: plain words on the capture screen.
const api = vi.hoisted(() => ({ apiGet: vi.fn(), apiPost: vi.fn(), uploadEvidence: vi.fn() }));
vi.mock("./api/client", () => api);

function renderCapture() {
  api.apiGet.mockResolvedValue([{ id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" }]);
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>
        <HouseholdProvider>
          <CapturePage />
        </HouseholdProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

function renderForm() {
  return render(
    <MemoryRouter>
      <AssetForm householdId="h1" onCreated={() => {}} />
    </MemoryRouter>
  );
}

describe("SG-325 P11 capture plain words", () => {
  test("the page heading reads Add an item", async () => {
    renderCapture();

    expect(await screen.findByRole("heading", { name: "Add an item" })).toBeInTheDocument();
    expect(screen.queryByText("Capture — Manual Create")).not.toBeInTheDocument();
  });

  test("the submit button reads Add to catalog", () => {
    renderForm();

    expect(screen.getByRole("button", { name: "Add to catalog" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Create asset" })).not.toBeInTheDocument();
  });

  test("the filename hint uses plain words at 13px", () => {
    renderForm();

    const hint = screen.getByText("Leave it blank and we use the photo's file name");
    expect(hint.style.fontSize).toBe("13px");
    expect(screen.queryByText(/we use the photo's filename$/i)).not.toBeInTheDocument();
  });

  test("the kind select reads not chosen yet", () => {
    renderForm();

    expect(screen.getByRole("option", { name: "not chosen yet" })).toBeInTheDocument();
    expect(screen.queryByRole("option", { name: "unknown" })).not.toBeInTheDocument();
  });
});
