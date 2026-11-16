import { describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ProductCard, type CatalogProduct } from "./components/catalog/ProductCard";
import { assetToProductItem } from "./types/product";
import { labelAssetType } from "./lib/labels";
import type { Asset } from "./api/types";

vi.mock("./api/client", () => ({ apiGet: vi.fn(), apiPatch: vi.fn() }));

// SG-330 R5: the item is built the way CatalogPage builds it — the real Asset
// shape through assetToProductItem plus the use-by join (date + days).
function cardItem(asset: Asset, useBy: string | null, daysRemaining: number | null): CatalogProduct {
  const base = assetToProductItem(asset);
  return { ...base, useBy, daysRemaining };
}

function asset(id: string, name: string): Asset {
  return {
    id,
    household_id: "h1",
    display_name: name,
    asset_type: "product",
    status: "ACTIVE",
    quantity: null,
    unit: null,
    condition: null,
    version: 1,
    created_at: "2026-09-10T00:00:00Z",
    updated_at: null,
  };
}

function renderCard(item: CatalogProduct) {
  return render(
    <MemoryRouter>
      <ProductCard item={item} householdId="h1" />
    </MemoryRouter>
  );
}

describe("SG-330 R5 photo-first card", () => {
  test("a past date reads Past its date with the day and month, no status chrome", () => {
    const { unmount } = renderCard(cardItem(asset("a-past", "Milk"), "2026-10-27", -5));
    expect(screen.getByTestId("product-date-wide")).toHaveTextContent("Past its date · 27 Oct");
    expect(screen.getByTestId("product-date-narrow")).toHaveTextContent("Past · 27 Oct");
    expect(screen.queryByTestId("color-dots")).not.toBeInTheDocument();
    expect(screen.queryByTestId("failed-warning")).not.toBeInTheDocument();
    expect(screen.queryByTestId("title-error-icon")).not.toBeInTheDocument();
    expect(screen.queryByTestId("product-category")).not.toBeInTheDocument();
    expect(screen.queryByText("Photo only")).not.toBeInTheDocument();
    unmount();
  });

  test("this week reads Use by with the countdown in soon colours", () => {
    renderCard(cardItem(asset("a-soon", "Yogurt"), "2026-11-21", 5));
    expect(screen.getByTestId("product-date-wide")).toHaveTextContent("Use by 21 Nov · 5 days");
    expect(screen.getByTestId("product-date-narrow")).toHaveTextContent("21 Nov");
  });

  test("a later date reads Use by with the full date in ink", () => {
    const { unmount } = renderCard(cardItem(asset("a-later", "Olive Oil"), "2030-05-06", 100));
    expect(screen.getByTestId("product-date-wide")).toHaveTextContent("Use by 6 May 2030");
    expect(screen.getByTestId("product-date-narrow")).toHaveTextContent("6 May 2030");
    unmount();
  });

  test("no date reads No date yet, and the kind of item shows below", () => {
    renderCard(cardItem(asset("a-none", "Beans"), null, null));
    expect(screen.getByTestId("product-date-wide")).toHaveTextContent("No date yet");
    expect(screen.getByTestId("product-date-narrow")).toHaveTextContent("No date");
    expect(screen.getByTestId("product-kind")).toHaveTextContent(labelAssetType("product"));
  });

  test("the photo tile fills the column on the tile ground with no border", () => {
    renderCard(cardItem(asset("a-later", "Olive Oil"), "2030-05-06", 100));
    const card = screen.getByTestId("product-card");
    expect(card.getAttribute("style") ?? "").toContain("none");
    expect(card.style.borderStyle).not.toBe("solid");
    const well = screen.getByTestId("product-card-well");
    expect(well.style.aspectRatio).toBe("1 / 1");
    expect(well.style.backgroundColor).toContain("tile");
    expect(well.style.borderStyle).not.toBe("solid");
  });
});
