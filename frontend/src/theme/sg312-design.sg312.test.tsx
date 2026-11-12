// @ts-expect-error: node:fs is available in the vitest runtime; @types/node is intentionally not a project dependency
import { readFileSync } from "node:fs";
// @ts-expect-error: node:path is available in the vitest runtime; @types/node is intentionally not a project dependency
import { join } from "node:path";
import { afterEach, describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "../App";
import { ThemeProvider } from "./ThemeProvider";

// @ts-expect-error: __dirname is available in the vitest runtime; @types/node is intentionally not a project dependency
const root = join(__dirname, "..", "..", "..");
function src(path: string): string {
  return readFileSync(join(root, path), "utf8");
}
const tokensCss: string = src("frontend/src/theme/tokens.css");

const api = vi.hoisted(() => ({ apiGet: vi.fn(), apiPost: vi.fn() }));
vi.mock("../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../api/client")>()),
  ...api,
}));

afterEach(() => {
  vi.clearAllMocks();
});

function renderApp(path: string) {
  api.apiGet.mockResolvedValue({ items: [], next_cursor: null, total: 0 });
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ThemeProvider>
        <MemoryRouter initialEntries={[path]}>
          <App />
        </MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

describe("SG-312 paper ground on every page (I1)", () => {
  test("the body paints --paper", () => {
    expect(tokensCss).toMatch(/body\s*\{[^}]*background-color:\s*hsl\(var\(--paper\)\)/);
  });
  test("the body no longer paints --background", () => {
    expect(tokensCss).not.toMatch(/body\s*\{[^}]*background-color:\s*hsl\(var\(--background\)\)/);
  });
  test("the app shell wrapper paints --paper inline, not the bg-background class", () => {
    renderApp("/capture");
    const shell = document.querySelector("nav")?.parentElement;
    expect(shell).toBeTruthy();
    expect(shell?.getAttribute("style") ?? "").toContain("var(--paper)");
    expect(shell?.className ?? "").not.toContain("bg-background");
  });
});

describe("SG-312 one font in controls (I2)", () => {
  test("tokens.css sets font: inherit on button, input, select and textarea", () => {
    expect(tokensCss).toMatch(/button,\s*input,\s*select,\s*textarea\s*\{[^}]*font:\s*inherit/);
  });
  test("a rendered button is matched by that inherit-font rule", () => {
    const style = document.createElement("style");
    style.textContent = tokensCss;
    document.head.appendChild(style);
    const button = document.createElement("button");
    document.body.appendChild(button);
    const rules = Array.from(style.sheet?.cssRules ?? []) as CSSStyleRule[];
    const hit = rules.find(
      (rule) => rule.style?.getPropertyValue("font") === "inherit" && button.matches(rule.selectorText)
    );
    expect(hit).toBeDefined();
    button.remove();
    style.remove();
  });
});

describe("SG-312 Menu only where the links hide (I4)", () => {
  test("the Menu button carries the nav-menu-toggle class", () => {
    renderApp("/capture");
    expect(screen.getByRole("button", { name: "Menu" })).toHaveClass("nav-menu-toggle");
  });
  test("tokens.css hides nav-menu-toggle at every width by default", () => {
    expect(tokensCss).toMatch(/\.nav-menu-toggle\s*\{\s*display:\s*none;\s*\}/);
  });
});
