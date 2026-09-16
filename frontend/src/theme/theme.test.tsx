import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { ThemeProvider, useTheme } from "./ThemeProvider";
import { ThemeToggle } from "./ThemeToggle";
import tokensCss from "./tokens.css?raw";

function mockMatchMedia(matches: boolean) {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    configurable: true,
    value: (query: string) => ({
      matches,
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }),
  });
}

function Probe() {
  const { theme, resolvedTheme, setTheme } = useTheme();
  return (
    <div>
      <span data-testid="theme">{theme}</span>
      <span data-testid="resolved">{resolvedTheme}</span>
      <button data-testid="set-dark" onClick={() => setTheme("dark")}>
        dark
      </button>
      <button data-testid="set-light" onClick={() => setTheme("light")}>
        light
      </button>
      <ThemeToggle />
    </div>
  );
}

function darkBlock(css: string): string {
  const match = css.match(/\.dark\s*\{([\s\S]*?)\}/);
  if (!match) throw new Error("tokens.css has no .dark block");
  return match[1];
}

function tokenValue(css: string, token: string): string {
  const match = css.match(new RegExp(`--${token}:\\s*([^;]+);`));
  if (!match) throw new Error(`tokens.css has no --${token}`);
  return match[1].trim();
}

function hslToHex(hsl: string): string {
  const match = hsl.match(/(-?[\d.]+)\s+([\d.]+)%\s+([\d.]+)%/);
  if (!match) throw new Error(`unparsable hsl triplet: ${hsl}`);
  const h = parseFloat(match[1]) / 360;
  const s = parseFloat(match[2]) / 100;
  const l = parseFloat(match[3]) / 100;
  const hue2rgb = (p: number, q: number, t: number) => {
    if (t < 0) t += 1;
    if (t > 1) t -= 1;
    if (t < 1 / 6) return p + (q - p) * 6 * t;
    if (t < 1 / 2) return q;
    if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
    return p;
  };
  let r: number;
  let g: number;
  let b: number;
  if (s === 0) {
    r = g = b = l;
  } else {
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    r = hue2rgb(p, q, h + 1 / 3);
    g = hue2rgb(p, q, h);
    b = hue2rgb(p, q, h - 1 / 3);
  }
  const to = (x: number) => Math.round(x * 255).toString(16).padStart(2, "0").toUpperCase();
  return `#${to(r)}${to(g)}${to(b)}`;
}

describe("ThemeProvider", () => {
  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.className = "";
    mockMatchMedia(false);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("defaults to system and applies the light class when the OS prefers light", () => {
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>
    );
    expect(screen.getByTestId("theme").textContent).toBe("system");
    expect(document.documentElement.classList.contains("light")).toBe(true);
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  test("OS dark preference applies .dark to <html>", () => {
    mockMatchMedia(true);
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>
    );
    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(document.documentElement.classList.contains("light")).toBe(false);
  });

  test("explicit dark flips the class and persists to localStorage", () => {
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>
    );
    fireEvent.click(screen.getByTestId("set-dark"));
    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(window.localStorage.getItem("sg-theme")).toBe("dark");
  });

  test("a stored theme is restored on mount", () => {
    window.localStorage.setItem("sg-theme", "dark");
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>
    );
    expect(screen.getByTestId("resolved").textContent).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });
});

describe("ThemeToggle", () => {
  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.className = "";
    mockMatchMedia(false);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("shows Moon in light mode with an accessible label", () => {
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>
    );
    const button = screen.getByRole("button", { name: /switch to dark theme/i });
    expect(button.querySelector("svg")?.getAttribute("class")).toContain("lucide-moon");
    expect(button).toHaveClass("focus-ring");
  });

  test("clicking the toggle switches to Sun and saves the choice", () => {
    render(
      <ThemeProvider>
        <Probe />
      </ThemeProvider>
    );
    fireEvent.click(screen.getByRole("button", { name: /switch to dark theme/i }));
    const button = screen.getByRole("button", { name: /switch to light theme/i });
    expect(button.querySelector("svg")?.getAttribute("class")).toContain("lucide-sun");
    expect(window.localStorage.getItem("sg-theme")).toBe("dark");
  });
});

describe("tokens.css", () => {
  test("declares the exact DQ3 dark elevation layers", () => {
    const dark = darkBlock(tokensCss);
    expect(hslToHex(tokenValue(dark, "background"))).toBe("#0F0E0D");
    expect(hslToHex(tokenValue(dark, "card"))).toBe("#1C1A18");
    expect(hslToHex(tokenValue(dark, "card-muted"))).toBe("#262320");
    expect(hslToHex(tokenValue(dark, "border"))).toBe("#2C2926");
  });

  test("light canvas is Stone-50", () => {
    expect(hslToHex(tokenValue(tokensCss, "background"))).toBe("#FAFAF9");
  });

  test("every colour rule references a token (no arbitrary hex)", () => {
    expect(tokensCss).not.toMatch(/#[0-9a-fA-F]{3,8}\b/);
  });

  test("defines utilities for each token as hsl(var(--token))", () => {
    for (const token of [
      "background",
      "foreground",
      "card",
      "card-muted",
      "border",
      "muted",
      "muted-foreground",
      "primary",
      "primary-foreground",
    ]) {
      expect(tokensCss).toContain(`hsl(var(--${token}))`);
    }
  });
});
