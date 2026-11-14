import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ProductGrid } from "./components/catalog/ProductGrid";

describe("SG-324 P4 catalog table", () => {
  test("Dimensions/Specs column is gone from the table", () => {
    render(
      <MemoryRouter>
        <ProductGrid
          items={[
            {
              id: "a1",
              name: "Olive Oil",
              category: "product",
              tags: [],
              dateAdded: new Date().toISOString(),
              status: "raw",
              metadata: { dimensions: "10x20" },
            },
          ]}
          density="table"
          householdId="hh"
        />
      </MemoryRouter>
    );
    expect(screen.queryByText("Dimensions/Specs")).toBeNull();
    expect(screen.queryByText("DIMENSIONS/SPECS")).toBeNull();
    expect(screen.queryByText("10x20")).toBeNull();
  });

  test("row actions carry More actions for the item name with a title", () => {
    render(
      <MemoryRouter>
        <ProductGrid
          items={[
            {
              id: "a1",
              name: "Olive Oil",
              category: "product",
              tags: [],
              dateAdded: new Date().toISOString(),
              status: "raw",
              metadata: {},
            },
          ]}
          density="table"
          householdId="hh"
        />
      </MemoryRouter>
    );
    const btn = screen.getByRole("button", { name: "More actions for Olive Oil" });
    expect(btn).toHaveAttribute("title", "More actions for Olive Oil");
  });
});
