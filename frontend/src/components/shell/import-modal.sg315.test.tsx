import { describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AssetImportModal } from "./AssetImportModal";

function renderModal() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/"]}>
        <AssetImportModal householdId="h1" onClose={vi.fn()} />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("SG-315 drop-zone highlight (SG-307 dropped the dragOver read)", () => {
  test("the drop zone border turns --primary while a file is dragged over it and returns to --line on drag-leave", () => {
    renderModal();
    const zone = screen.getByTestId("import-dropzone");
    expect(zone.style.borderColor).toBe("hsl(var(--line))");

    fireEvent.dragOver(zone);
    expect(zone.style.borderColor).toBe("hsl(var(--primary))");

    fireEvent.dragLeave(zone);
    expect(zone.style.borderColor).toBe("hsl(var(--line))");
  });
});
