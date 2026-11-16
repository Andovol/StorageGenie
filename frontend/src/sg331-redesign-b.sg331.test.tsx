import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ProductGrid } from "./components/catalog/ProductGrid";

// SG-331 T7: CSS `gap` is row column — wide 40px 24px, narrow 16px 8px.
function item(id: string, name: string) {
  return {
    id,
    name,
    category: "product",
    tags: [],
    dateAdded: "2026-09-10T00:00:00Z",
    status: "raw" as const,
    metadata: {},
  };
}

describe("SG-331 T7 grid gaps are row column", () => {
  test("wide grid uses 40px 24px and narrow uses 16px 8px", () => {
    const { unmount } = render(
      <MemoryRouter>
        <ProductGrid items={[item("a", "Milk")]} density="grid" householdId="h1" perRow={5} narrow={false} />
      </MemoryRouter>
    );
    expect(screen.getByTestId("catalog-grid").style.gap).toBe("40px 24px");
    unmount();
    render(
      <MemoryRouter>
        <ProductGrid items={[item("a", "Milk")]} density="grid" householdId="h1" perRow={3} narrow />
      </MemoryRouter>
    );
    expect(screen.getByTestId("catalog-grid").style.gap).toBe("16px 8px");
  });
});
