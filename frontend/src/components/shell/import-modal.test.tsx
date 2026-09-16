import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AssetImportModal } from "./AssetImportModal";
import { AppHeader } from "./AppHeader";
import { ProductGrid } from "../catalog/ProductGrid";
import { InboxPage } from "../../routes/InboxPage";
import { ThemeProvider } from "../../theme/ThemeProvider";

// The transport boundary is mocked; the app API is the only external system this slice talks to.
const api = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  uploadEvidence: vi.fn(),
  resolveReviewTask: vi.fn(),
}));
vi.mock("../../api/client", () => api);
vi.mock("../../hooks/useAssets", () => ({
  useHouseholds: () => ({
    data: [{ id: "h1", name: "Home", created_at: "2026-09-01T00:00:00Z" }],
  }),
}));

function imageFile(name: string, type = "image/png"): File {
  return new File([new Uint8Array([0x89, 0x50, 0x4e, 0x47])], name, { type });
}

function evidence(id: string) {
  return { id, sha256: "deadbeef", storage_key: `key-${id}`, size_bytes: 4 };
}

function newClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function renderModal(onClose = vi.fn()) {
  return render(
    <MemoryRouter initialEntries={["/"]}>
      <Routes>
        <Route path="/" element={<AssetImportModal householdId="h1" onClose={onClose} />} />
        <Route path="/inbox" element={<div>inbox probe</div>} />
      </Routes>
    </MemoryRouter>
  );
}

function dropFiles(...files: File[]) {
  fireEvent.drop(screen.getByTestId("import-dropzone"), { dataTransfer: { files } });
}

beforeEach(() => {
  api.apiGet.mockReset();
  api.apiPost.mockReset();
  api.uploadEvidence.mockReset();
  api.resolveReviewTask.mockReset();
  api.apiGet.mockResolvedValue({ items: [], next_cursor: null, total: 0 });
  api.uploadEvidence.mockImplementation((householdId: string, file: File) =>
    Promise.resolve(evidence(`ev-${file.name}`))
  );
  api.apiPost.mockImplementation((path: string) =>
    path === "/v1/imports"
      ? Promise.resolve({ id: "job-1" })
      : Promise.resolve({ id: "job-1", state: "RUNNING" })
  );
});

afterEach(() => {
  vi.clearAllMocks();
});

describe("AssetImportModal staging", () => {
  test("drop stages accepted files as Ready with a live count", () => {
    renderModal();
    dropFiles(imageFile("a.png"), imageFile("b.jpg", "image/jpeg"));

    expect(screen.getAllByTestId("queue-item")).toHaveLength(2);
    expect(screen.getByText("a.png")).toBeInTheDocument();
    expect(screen.getAllByText("Ready")).toHaveLength(2);
    expect(screen.getByTestId("queue-count")).toHaveTextContent("Pending queue (2)");
    expect(screen.getByRole("button", { name: "Process 2 Items" })).toBeEnabled();
  });

  test("file select stages files", () => {
    renderModal();
    const input = screen.getByLabelText("Choose image files") as HTMLInputElement;
    Object.defineProperty(input, "files", { value: [imageFile("chosen.png")], configurable: true });
    fireEvent.change(input);

    expect(screen.getAllByTestId("queue-item")).toHaveLength(1);
    expect(screen.getByText("chosen.png")).toBeInTheDocument();
  });

  test("window paste stages clipboard files", () => {
    renderModal();
    fireEvent.paste(screen.getByTestId("import-dropzone"), {
      clipboardData: { files: [imageFile("pasted.png")] },
    });

    expect(screen.getAllByTestId("queue-item")).toHaveLength(1);
    expect(screen.getByText("pasted.png")).toBeInTheDocument();
  });

  test("a rejected file is named and skipped, never silently dropped", () => {
    renderModal();
    dropFiles(imageFile("good.png"), imageFile("bad.gif", "image/gif"));

    const rejected = screen.getByTestId("rejected-files");
    expect(rejected).toHaveTextContent("bad.gif");
    expect(rejected).toHaveTextContent(/unsupported type image\/gif/i);
    expect(screen.getAllByTestId("queue-item")).toHaveLength(1);
    expect(screen.getByText("good.png")).toBeInTheDocument();
  });

  test("Remove drops one staged file and updates the live count", () => {
    renderModal();
    dropFiles(imageFile("a.png"), imageFile("b.png"));

    fireEvent.click(screen.getByRole("button", { name: "Remove a.png" }));
    expect(screen.getAllByTestId("queue-item")).toHaveLength(1);
    expect(screen.getByRole("button", { name: "Process 1 Item" })).toBeEnabled();
  });

  test("Process is disabled with an empty queue", () => {
    renderModal();
    expect(screen.getByTestId("queue-empty")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Process 0 Items" })).toBeDisabled();
  });
});

describe("AssetImportModal processing", () => {
  test("checked (default): one import with a UUID Idempotency-Key, then run, then route to /inbox", async () => {
    renderModal();
    dropFiles(imageFile("a.png"), imageFile("b.png"));
    expect(screen.getByRole("checkbox", { name: /automatically detect/i })).toBeChecked();
    expect(screen.getByTestId("auto-detect-help")).toHaveTextContent(/run immediately/i);

    fireEvent.click(screen.getByRole("button", { name: "Process 2 Items" }));

    await waitFor(() => expect(api.uploadEvidence).toHaveBeenCalledTimes(2));
    expect(api.uploadEvidence.mock.calls.map(([householdId]) => householdId)).toEqual(["h1", "h1"]);

    await waitFor(() =>
      expect(api.apiPost).toHaveBeenNthCalledWith(
        1,
        "/v1/imports",
        { evidence_ids: ["ev-a.png", "ev-b.png"], config: {} },
        { household_id: "h1" },
        {
          "Idempotency-Key": expect.stringMatching(
            /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/
          ),
        }
      )
    );
    await waitFor(() =>
      expect(api.apiPost).toHaveBeenNthCalledWith(2, "/v1/imports/job-1/run", {}, { household_id: "h1" })
    );
    expect(await screen.findByText("inbox probe")).toBeInTheDocument();
  });

  test("unchecked: creates the job WITHOUT running it and states it waits in the Inbox", async () => {
    renderModal();
    dropFiles(imageFile("a.png"));
    fireEvent.click(screen.getByRole("checkbox"));
    expect(screen.getByTestId("auto-detect-help")).toHaveTextContent(/waits in the Inbox/i);

    fireEvent.click(screen.getByRole("button", { name: "Process 1 Item" }));

    await waitFor(() => expect(api.apiPost).toHaveBeenCalledTimes(1));
    expect(api.apiPost).toHaveBeenCalledWith(
      "/v1/imports",
      { evidence_ids: ["ev-a.png"], config: {} },
      { household_id: "h1" },
      { "Idempotency-Key": expect.any(String) }
    );
    expect(api.apiPost).not.toHaveBeenCalledWith(
      "/v1/imports/job-1/run",
      expect.anything(),
      expect.anything()
    );
    expect(await screen.findByText("inbox probe")).toBeInTheDocument();
  });

  test("the created job is visible on the /inbox screen after Process", async () => {
    api.apiGet.mockImplementation((path: string) => {
      if (path === "/v1/jobs") {
        return Promise.resolve({
          items: [
            {
              id: "job-1",
              job_type: "import",
              state: "RUNNING",
              household_id: "h1",
              created_at: null,
              updated_at: null,
            },
          ],
          next_cursor: null,
          total: 1,
        });
      }
      if (path === "/v1/imports/job-1") {
        return Promise.resolve({
          id: "job-1",
          job_type: "import",
          state: "RUNNING",
          household_id: "h1",
          steps: [],
          progress: { completed: 0, total: 0, failed: 0, pending: 0 },
          errors: [],
        });
      }
      return Promise.resolve({ items: [], next_cursor: null, total: 0 });
    });

    render(
      <QueryClientProvider client={newClient()}>
        <MemoryRouter initialEntries={["/"]}>
          <Routes>
            <Route path="/" element={<AssetImportModal householdId="h1" onClose={vi.fn()} />} />
            <Route path="/inbox" element={<InboxPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    dropFiles(imageFile("a.png"));
    fireEvent.click(screen.getByRole("button", { name: "Process 1 Item" }));

    expect(await screen.findByText("Import job-1")).toBeInTheDocument();
    expect(api.apiGet).toHaveBeenCalledWith("/v1/jobs", { household_id: "h1" });
  });
});

describe("AssetImportModal dialog behaviour", () => {
  test("Cancel discards staged bytes, uploads nothing, and closes", () => {
    const onClose = vi.fn();
    renderModal(onClose);
    dropFiles(imageFile("a.png"));
    expect(screen.getAllByTestId("queue-item")).toHaveLength(1);

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onClose).toHaveBeenCalledTimes(1);
    expect(api.uploadEvidence).not.toHaveBeenCalled();
    expect(screen.getByTestId("queue-empty")).toBeInTheDocument();
  });

  test("Esc closes the dialog", () => {
    const onClose = vi.fn();
    renderModal(onClose);
    fireEvent.keyDown(document, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  test("focus moves in on open and returns to the invoking element on unmount", async () => {
    const invoker = document.createElement("button");
    invoker.textContent = "open";
    document.body.appendChild(invoker);
    invoker.focus();

    const { unmount } = renderModal();
    await waitFor(() =>
      expect(document.activeElement).toBe(screen.getByRole("button", { name: "Close import dialog" }))
    );

    unmount();
    expect(document.activeElement).toBe(invoker);
    invoker.remove();
  });
});

describe("CTA wiring (G2)", () => {
  test("the header Import Asset link opens the dialog instead of routing to /capture", () => {
    render(
      <ThemeProvider>
        <MemoryRouter initialEntries={["/"]}>
          <Routes>
            <Route
              path="/"
              element={
                <>
                  <AppHeader loadedCount={0} searchValue="" onSearchChange={vi.fn()} />
                  <div>catalog probe</div>
                </>
              }
            />
            <Route path="/capture" element={<div>capture probe</div>} />
          </Routes>
        </MemoryRouter>
      </ThemeProvider>
    );

    fireEvent.click(screen.getByRole("link", { name: /import asset/i }));

    expect(screen.getByRole("dialog", { name: "Import assets" })).toBeInTheDocument();
    expect(screen.getByText("catalog probe")).toBeInTheDocument();
    expect(screen.queryByText("capture probe")).not.toBeInTheDocument();
  });

  test("the empty-state Import New Item CTA opens the dialog instead of routing", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<ProductGrid items={[]} density="grid" householdId="h1" />} />
          <Route path="/capture" element={<div>capture probe</div>} />
        </Routes>
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText(/import new item/i));

    expect(screen.getByRole("dialog", { name: "Import assets" })).toBeInTheDocument();
    expect(screen.queryByText("capture probe")).not.toBeInTheDocument();
  });
});
