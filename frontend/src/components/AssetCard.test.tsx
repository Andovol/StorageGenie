import { describe, test, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AssetCard } from "./AssetCard";

describe("AssetCard", () => {
  test("renders display_name and type", () => {
    render(
      <MemoryRouter>
        <AssetCard asset={{ id: "1", household_id: "h1", display_name: "Hammer", asset_type: "equipment", status: "ACTIVE", quantity: null, unit: null, condition: null, version: 1, created_at: new Date().toISOString(), updated_at: null } as never} householdId="h1" />
      </MemoryRouter>
    );
    expect(screen.getByText("Hammer")).toBeInTheDocument();
  });
});
