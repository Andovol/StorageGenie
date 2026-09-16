import { assetToProductItem, type ProductStatus } from "../../types/product";
import type { Asset } from "../../api/types";
import type { CatalogProduct } from "./ProductCard";

/**
 * Deterministic inline SVG placeholders: no network, no committed binaries.
 * The label/fill are data, not design tokens; the card chrome itself is
 * token-class driven.
 */
function svgDataUri(label: string, fill: string): string {
  const svg =
    '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">' +
    `<rect width="120" height="120" rx="12" fill="${fill}"/>` +
    `<text x="60" y="64" font-family="monospace" font-size="11" text-anchor="middle" fill="#ffffff">${label}</text>` +
    "</svg>";
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

const NOW_MS = Date.now();
const daysAgo = (days: number): string => new Date(NOW_MS - days * 86_400_000).toISOString();

type MockSpec = {
  id: string;
  name: string;
  assetType: string;
  daysAdded: number;
  status: ProductStatus;
  cutout?: { label: string; fill: string };
  scene?: { label: string; fill: string };
  metadata?: CatalogProduct["metadata"];
};

const MOCK_SPECS: MockSpec[] = [
  {
    id: "mock-drill",
    name: "Cordless Drill",
    assetType: "Hardware & Tools",
    daysAdded: 2,
    status: "raw",
    cutout: { label: "DRL", fill: "#1f2937" },
    metadata: { dimensions: "30 x 8 x 22 cm", primaryColors: ["#1f2937", "#f59e0b"] },
  },
  {
    id: "mock-mug",
    name: "Ceramic Mug Set",
    assetType: "Home & Decor",
    daysAdded: 4,
    status: "processed",
    cutout: { label: "MUG", fill: "#2563eb" },
    metadata: { dimensions: "12 x 9 x 9 cm", primaryColors: ["#e5e7eb", "#2563eb"] },
  },
  {
    id: "mock-shirt",
    name: "Linen Shirt",
    assetType: "Apparel & Textiles",
    daysAdded: 6,
    status: "rendered",
    cutout: { label: "SHT", fill: "#a8a29e" },
    scene: { label: "SHT", fill: "#0f766e" },
    metadata: { material: "100% linen", primaryColors: ["#f5f5f4"] },
  },
  {
    id: "mock-hub",
    name: "USB-C Hub",
    assetType: "Electronics & Gadgets",
    daysAdded: 1,
    status: "failed",
    cutout: { label: "HUB", fill: "#111827" },
    metadata: { dimensions: "10 x 4 x 1.5 cm", primaryColors: ["#111827"] },
  },
  {
    id: "mock-boxes",
    name: "Moving Boxes (5-pack)",
    assetType: "Packaging & Materials",
    daysAdded: 9,
    status: "raw",
    cutout: { label: "BOX", fill: "#b45309" },
    metadata: { dimensions: "50 x 40 x 40 cm" },
  },
  {
    id: "mock-mystery",
    name: "Mystery Item",
    assetType: "unknown",
    daysAdded: 12,
    status: "processed",
    cutout: { label: "?", fill: "#52525b" },
  },
  {
    id: "mock-scarf",
    name: "Wool Scarf",
    assetType: "Apparel & Textiles",
    daysAdded: 20,
    status: "rendered",
    cutout: { label: "SCF", fill: "#7c3aed" },
    scene: { label: "SCF", fill: "#6d28d9" },
    metadata: { material: "Merino wool", primaryColors: ["#7c3aed", "#db2777"] },
  },
  {
    id: "mock-lamp",
    name: "Desk Lamp",
    assetType: "Home & Decor",
    daysAdded: 33,
    status: "raw",
    cutout: { label: "LMP", fill: "#d97706" },
    metadata: { primaryColors: ["#fbbf24"] },
  },
];

function mockAsset(spec: MockSpec): Asset {
  return {
    id: spec.id,
    household_id: "h1",
    display_name: spec.name,
    asset_type: spec.assetType,
    status: "ACTIVE",
    quantity: null,
    unit: null,
    condition: null,
    version: 1,
    created_at: daysAgo(spec.daysAdded),
    updated_at: null,
  };
}

function buildMockProduct(spec: MockSpec): CatalogProduct {
  const item = assetToProductItem(mockAsset(spec));
  return {
    ...item,
    status: spec.status,
    metadata: spec.metadata ?? {},
    ...(spec.cutout ? { cutoutUrl: svgDataUri(spec.cutout.label, spec.cutout.fill) } : {}),
    ...(spec.scene ? { sceneUrl: svgDataUri(spec.scene.label, spec.scene.fill) } : {}),
  };
}

export const MOCK_PRODUCTS: CatalogProduct[] = MOCK_SPECS.map(buildMockProduct);
