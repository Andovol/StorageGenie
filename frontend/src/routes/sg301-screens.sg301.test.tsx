// @ts-expect-error: node:fs is available in the vitest runtime; @types/node is intentionally not a project dependency
import { readFileSync } from "node:fs";
// @ts-expect-error: node:path is available in the vitest runtime; @types/node is intentionally not a project dependency
import { join } from "node:path";
import { describe, expect, test, vi, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "../App";
import { HouseholdProvider } from "../hooks/HouseholdContext";
import { ThemeProvider } from "../theme/ThemeProvider";

// @ts-expect-error: __dirname is available in the vitest runtime; @types/node is intentionally not a project dependency
const root = join(__dirname, "..", "..", "..");
function src(path: string): string {
  return readFileSync(join(root, path), "utf8");
}

describe("SG-301 font", () => {
  test("--font-sans begins with Instrument Sans Variable", () => {
    const css = src("frontend/src/theme/tokens.css");
    expect(css).toMatch(/--font-sans:\s*"Instrument Sans Variable",/);
  });
  test("app entry imports the self-hosted font once", () => {
    const main = src("frontend/src/main.tsx");
    expect(main).toContain('@fontsource-variable/instrument-sans"');
  });
});

describe("SG-301 no developer copy in source", () => {
  test("Inbox has no raw COMPLETED state", () => {
    expect(src("frontend/src/routes/InboxPage.tsx")).not.toContain("COMPLETED");
  });
  test("Inbox has no Task id line", () => {
    expect(src("frontend/src/routes/InboxPage.tsx")).not.toContain("Task {");
  });
  test("Inbox has no unknown subject", () => {
    expect(src("frontend/src/routes/InboxPage.tsx")).not.toContain("unknown subject");
  });
  test("Expiry has no blueprint sentence", () => {
    expect(src("frontend/src/routes/ExpiryPage.tsx")).not.toContain("blueprint");
  });
  test("Expiry has no served stream sentence", () => {
    expect(src("frontend/src/routes/ExpiryPage.tsx")).not.toContain("served");
  });
  test("Expiry keeps one plain help line", () => {
    expect(src("frontend/src/routes/ExpiryPage.tsx")).toContain("Food and other dated things, soonest first.");
  });
  test("Asset page renders no If-Match text", () => {
    expect(src("frontend/src/routes/AssetDetailPage.tsx")).not.toContain("Uses If-Match");
  });
  test("header has no Phase 0 line", () => {
    expect(src("frontend/src/App.tsx")).not.toContain("Phase 0");
  });
});

const household = { id: "hh-sg301", name: "SG301 home", created_at: "2026-01-01" };
const api = vi.hoisted(() => ({ apiGet: vi.fn(), apiPost: vi.fn(), resolveReviewTask: vi.fn(), fetchAiSettings: vi.fn() }));
vi.mock("../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../api/client")>()),
  ...api,
}));
vi.mock("../hooks/useAssets", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../hooks/useAssets")>()),
  useHouseholds: () => ({ data: [household] }),
}));

afterEach(() => { vi.clearAllMocks(); });

describe("SG-301 Inbox skipped step", () => {
  test("skipped output does not read Done", async () => {
    const { labelStepStatus } = await import("../lib/labels");
    const label = labelStepStatus({ id: "s", step_name: "EXTRACT", state: "COMPLETED", attempts: 1, input: null, output: { status: "skipped", reason: "consent_disabled" }, error: null });
    expect(label).toBe("Skipped (AI off)");
    expect(label).not.toBe("Done");
  });
});

describe("SG-301 header sizes", () => {
  test("header renders no text under 13px and no Phase 0", async () => {
    api.apiGet.mockResolvedValue({ items: [], next_cursor: null, total: 0 });
    const { container } = render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <ThemeProvider>
          <HouseholdProvider>
            <MemoryRouter initialEntries={["/settings"]}>
              <App />
            </MemoryRouter>
          </HouseholdProvider>
        </ThemeProvider>
      </QueryClientProvider>
    );
    expect(await screen.findByText("StorageGenie")).toBeInTheDocument();
    const nav = container.querySelector("nav");
    expect(nav).not.toBeNull();
    expect((nav as HTMLElement).textContent || "").not.toMatch(/Phase 0/);
    const small = Array.from((nav as HTMLElement).querySelectorAll("[style]")).filter((el) => {
      const style = (el as HTMLElement).getAttribute("style") || "";
      const match = style.match(/font-size:\s*(\d+(?:\.\d+)?)px/);
      return match ? Number(match[1]) < 13 : false;
    });
    expect(small).toHaveLength(0);
  });
});
