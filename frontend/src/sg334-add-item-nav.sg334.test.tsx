import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";
import { ThemeProvider } from "./theme/ThemeProvider";

const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  buildUrl: (path: string) => path,
}));
vi.mock("./api/client", () => api);

function renderApp(initialEntries: string[]) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ThemeProvider>
        <MemoryRouter initialEntries={initialEntries}>
          <App />
        </MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

beforeEach(() => {
  window.localStorage.clear();
  api.apiGet.mockReset();
  api.apiPost.mockReset();
  api.apiPost.mockResolvedValue(undefined);
  api.apiGet.mockImplementation((path: string) => {
    if (path === "/v1/households") {
      return Promise.resolve([{ id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" }]);
    }
    if (path === "/v1/assets/facets") {
      return Promise.resolve({ asset_type: {}, status: {}, has_evidence: {} });
    }
    if (path === "/v1/saved-searches") {
      return Promise.resolve({ items: [] });
    }
    if (path === "/v1/assets") {
      return Promise.resolve({ items: [], next_cursor: null });
    }
    return Promise.resolve(null);
  });
});

afterEach(() => {
  vi.clearAllMocks();
});

describe("SG-334 non-catalog nav Add item", () => {
  test("the shared nav carries Add item in catalog-header colours and opens the import dialog", async () => {
    renderApp(["/capture"]);

    // Non-catalog route probe: CapturePage header proves we are off the catalog.
    expect(await screen.findByText("Add an item")).toBeInTheDocument();

    // Visible label and accessible name are Add item.
    const link = await screen.findByRole("link", { name: "Add item" });
    expect(link).toBeInTheDocument();

    // No product occurrence of the legacy name remains on this route.
    expect(screen.queryByRole("link", { name: "Import Asset" })).not.toBeInTheDocument();
    expect(screen.queryByText("Import Asset")).not.toBeInTheDocument();

    // Colours match the catalog header (AppHeader): --primary / --primary-foreground.
    const style = link.getAttribute("style") ?? "";
    expect(style).toContain("--primary");
    expect(style).toContain("--primary-foreground");

    // Clicking opens the import dialog instead of routing to /capture.
    fireEvent.click(link);
    expect(await screen.findByRole("dialog", { name: "Import assets" })).toBeInTheDocument();
    expect(screen.getByText("Add an item")).toBeInTheDocument();
  });
});
