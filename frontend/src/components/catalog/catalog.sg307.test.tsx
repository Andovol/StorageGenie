import { describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ProductCard } from "./ProductCard";
import { ProductGrid, formatRelativeDate } from "./ProductGrid";
import { labelProductStatus } from "../../lib/labels";
import { MOCK_PRODUCTS } from "./mockProducts";

vi.mock("../../api/client", () => ({ apiGet: vi.fn(), apiPatch: vi.fn() }));

function renderCard(status: "raw" | "processed" | "rendered" | "failed" = "raw") {
  const item = { ...MOCK_PRODUCTS[0], status };
  return render(
    <MemoryRouter>
      <ProductCard item={item} householdId="h1" />
    </MemoryRouter>
  );
}

describe("SG-307 catalog plain words, no mono, square paper", () => {
  test("status enums read as owner words through labels.ts", () => {
    expect(labelProductStatus("raw")).toBe("Photo only");
    expect(labelProductStatus("processed")).toBe("Cut-out ready");
    expect(labelProductStatus("rendered")).toBe("Scene ready");
    expect(labelProductStatus("failed")).toBe("Needs attention");
  });

  test("no font-mono class and no developer status string in the rendered card", () => {
    const { container, unmount } = renderCard("raw");
    expect(container.querySelector(".font-mono")).toBeNull();
    expect(screen.getByText("Photo only")).toBeInTheDocument();
    expect(screen.queryByText("Source Only")).toBeNull();
    expect(screen.queryByText("Cutout Extracted")).toBeNull();
    expect(screen.queryByText("Scene Rendered")).toBeNull();
    unmount();
  });

  test("every status renders its plain word with no mono", () => {
    for (const [status, word] of [
      ["raw", "Photo only"],
      ["processed", "Cut-out ready"],
      ["rendered", "Scene ready"],
      ["failed", "Needs attention"],
    ] as const) {
      const { container, unmount } = renderCard(status);
      expect(screen.getByText(word)).toBeInTheDocument();
      expect(container.querySelector(".font-mono")).toBeNull();
      unmount();
    }
  });

  test("time stamps are plain words in the body font, no mono", () => {
    const now = Date.parse("2026-09-16T12:00:00Z");
    expect(formatRelativeDate("2026-09-16T11:59:30Z", now)).toBe("just now");
    expect(formatRelativeDate("2026-09-16T11:30:00Z", now)).toBe("30 min ago");
    expect(formatRelativeDate("2026-09-16T06:00:00Z", now)).toBe("6 hours ago");
    expect(formatRelativeDate("2026-09-10T12:00:00Z", now)).toBe("6 days ago");
    const { container } = render(
      <MemoryRouter>
        <ProductGrid items={[MOCK_PRODUCTS[0]]} density="table" householdId="h1" />
      </MemoryRouter>
    );
    expect(container.querySelector(".font-mono")).toBeNull();
    expect(screen.queryByText(/^\d+m ago$/)).toBeNull();
    expect(screen.queryByText(/^\d+h ago$/)).toBeNull();
    expect(screen.queryByText(/^\d+d ago$/)).toBeNull();
  });

  test("the grid uses the tandpfun track rule", () => {
    render(
      <MemoryRouter>
        <ProductGrid items={MOCK_PRODUCTS} density="grid" householdId="h1" />
      </MemoryRouter>
    );
    const css = screen.getByTestId("catalog-grid-style").textContent ?? "";
    expect(css).toContain("repeat(auto-fill, minmax(165px, 1fr))");
  });

  test("the card and well are square on the paper, category is plain 13px", () => {
    renderCard("raw");
    const card = screen.getByTestId("product-card");
    expect(card.style.borderRadius).toMatch(/^0/);
    expect(card.style.backgroundColor).toContain("paper");
    const well = screen.getByTestId("product-card-well");
    expect(well.style.borderRadius).toMatch(/^0/);
    const chip = screen.getByTestId("product-category");
    expect(chip.textContent).toBe(MOCK_PRODUCTS[0].category);
    expect(chip.className).not.toContain("font-mono");
  });
});
