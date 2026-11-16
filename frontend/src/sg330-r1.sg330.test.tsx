// @ts-expect-error: node:fs is available in the vitest runtime; @types/node is intentionally not a project dependency
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";

const tokensCss = readFileSync("src/theme/tokens.css", "utf8");

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

function hslChannels(hsl: string): [number, number, number] {
  const match = hsl.match(/(-?[\d.]+)\s+([\d.]+)%\s+([\d.]+)%/);
  if (!match) throw new Error(`unparsable hsl triplet: ${hsl}`);
  const h = parseFloat(match[1]) / 360;
  const s = parseFloat(match[2]) / 100;
  const l = parseFloat(match[3]) / 100;
  if (s === 0) return [l, l, l];
  const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
  const p = 2 * l - q;
  const hue2rgb = (t: number) => {
    if (t < 0) t += 1;
    if (t > 1) t -= 1;
    if (t < 1 / 6) return p + (q - p) * 6 * t;
    if (t < 1 / 2) return q;
    if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
    return p;
  };
  return [hue2rgb(h + 1 / 3), hue2rgb(h), hue2rgb(h - 1 / 3)];
}

function relativeLuminance(hsl: string): number {
  const linear = hslChannels(hsl).map((c) =>
    c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
  );
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
}

function contrastRatio(a: string, b: string): number {
  const la = relativeLuminance(a);
  const lb = relativeLuminance(b);
  const [hi, lo] = la > lb ? [la, lb] : [lb, la];
  return (hi + 0.05) / (lo + 0.05);
}

// SG-330 R1: Midnight palette, exact values converted from the packet hexes.
const EXPECTED_LIGHT: Record<string, string> = {
  paper: "45 14.3% 94.5%",
  background: "45 14.3% 94.5%",
  card: "40 27.3% 97.8%",
  ink: "226.7 15.3% 11.6%",
  foreground: "226.7 15.3% 11.6%",
  "ink-muted": "225 5.9% 39.6%",
  "muted-foreground": "225 5.9% 39.6%",
  line: "228 7.2% 86.5%",
  border: "228 7.2% 86.5%",
  primary: "222.2 37.4% 19.4%",
  link: "222.2 37.4% 19.4%",
  "primary-foreground": "45 14.3% 94.5%",
  "past-bg": "10.9 47.8% 91%",
  "past-fg": "8.2 56.4% 30.6%",
  "soon-bg": "42.9 46.7% 88.2%",
  "soon-fg": "40 69.6% 22%",
  tile: "228 9.8% 90%",
};

const EXPECTED_DARK: Record<string, string> = {
  paper: "222.9 16.3% 8.4%",
  background: "222.9 16.3% 8.4%",
  card: "222 16.1% 12.2%",
  ink: "225 21.1% 92.5%",
  foreground: "225 21.1% 92.5%",
  "ink-muted": "224 8.8% 66.5%",
  "muted-foreground": "224 8.8% 66.5%",
  line: "221.5 14.3% 17.8%",
  border: "221.5 14.3% 17.8%",
  primary: "222.1 50.5% 81.8%",
  link: "222.1 50.5% 81.8%",
  "primary-foreground": "222.9 16.3% 8.4%",
  "past-bg": "0 30.3% 17.5%",
  "past-fg": "7.2 62.5% 84.3%",
  "soon-bg": "45 34.1% 16.1%",
  "soon-fg": "42.6 63.3% 78.6%",
  tile: "220 16.2% 14.5%",
};

function norm(hsl: string): string {
  return hsl.replace(/\s+/g, " ").trim();
}

describe("SG-330 R1 Midnight tokens", () => {
  test("light :root carries the exact Midnight values", () => {
    for (const [token, expected] of Object.entries(EXPECTED_LIGHT)) {
      expect(norm(tokenValue(tokensCss, token)), `--${token}`).toBe(norm(expected));
    }
  });

  test("dark .dark carries the exact Midnight values", () => {
    const dark = darkBlock(tokensCss);
    for (const [token, expected] of Object.entries(EXPECTED_DARK)) {
      expect(norm(tokenValue(dark, token)), `dark --${token}`).toBe(norm(expected));
    }
  });

  test("every text-on-ground pair clears WCAG AA 4.5:1, light and dark", () => {
    const dark = darkBlock(tokensCss);
    const pairs: [string, string, string][] = [
      ["light ink on ground", tokenValue(tokensCss, "ink"), tokenValue(tokensCss, "paper")],
      ["light muted on ground", tokenValue(tokensCss, "ink-muted"), tokenValue(tokensCss, "paper")],
      ["light link on ground", tokenValue(tokensCss, "link"), tokenValue(tokensCss, "paper")],
      ["light on-primary", tokenValue(tokensCss, "primary-foreground"), tokenValue(tokensCss, "primary")],
      ["light past", tokenValue(tokensCss, "past-fg"), tokenValue(tokensCss, "past-bg")],
      ["light soon", tokenValue(tokensCss, "soon-fg"), tokenValue(tokensCss, "soon-bg")],
      ["dark ink on ground", tokenValue(dark, "ink"), tokenValue(dark, "paper")],
      ["dark muted on ground", tokenValue(dark, "ink-muted"), tokenValue(dark, "paper")],
      ["dark link on ground", tokenValue(dark, "link"), tokenValue(dark, "paper")],
      ["dark on-primary", tokenValue(dark, "primary-foreground"), tokenValue(dark, "primary")],
      ["dark past", tokenValue(dark, "past-fg"), tokenValue(dark, "past-bg")],
      ["dark soon", tokenValue(dark, "soon-fg"), tokenValue(dark, "soon-bg")],
    ];
    for (const [name, fg, bg] of pairs) {
      const ratio = contrastRatio(fg, bg);
      // eslint-disable-next-line no-console
      console.log(`SG-330 contrast ${name}: ${ratio.toFixed(2)}:1`);
      expect(ratio, `${name} contrast ${ratio.toFixed(2)}:1`).toBeGreaterThanOrEqual(4.5);
    }
  });

  test("the five new tokens exist with utility classes", () => {
    for (const token of ["past-bg", "past-fg", "soon-bg", "soon-fg", "tile"]) {
      expect(tokensCss).toContain(`--${token}:`);
    }
    for (const cls of [".bg-past", ".text-past", ".bg-soon", ".text-soon", ".bg-tile"]) {
      expect(tokensCss).toContain(`${cls} {`);
    }
  });
});
