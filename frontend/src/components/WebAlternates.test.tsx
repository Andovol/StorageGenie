import { describe, expect, test } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { WebAlternates } from "./WebAlternates";
import type { WebAlternate } from "../api/types";

describe("WebAlternates", () => {
  test("renders null when alternates array is empty", () => {
    const { container } = render(<WebAlternates alternates={[]} />);
    expect(container.firstChild).toBeNull();
  });

  test("renders section title and alternate details when alternates are provided", () => {
    const alternates: WebAlternate[] = [
      {
        field: "brand",
        value: "Jacobs Cronat Gold",
        source_type: "web:OpenFoodFacts",
        source_url: "https://world.openfoodfacts.org/api/v2/search?search_terms=Jacobs",
        retrieved_at: "2026-09-25T00:00:00+00:00",
      },
    ];

    render(<WebAlternates alternates={alternates} />);

    const section = screen.getByRole("region", { name: "Web alternates" });
    expect(section).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 3, name: "Web alternates" })).toBeInTheDocument();
    // SG-301 G2: the label/web-conflict explanation sentence is removed on
    // purpose; the field/source read as plain words ("brand" is now "Brand",
    // "web:OpenFoodFacts" is now "Web").
    expect(section.textContent ?? "").not.toContain("keeps both values");

    const listItem = screen.getByTestId("web-alternate-brand");
    expect(within(listItem).getByText("Brand")).toBeInTheDocument();
    expect(within(listItem).getByText("Jacobs Cronat Gold")).toBeInTheDocument();
    expect(within(listItem).getByText("Web")).toBeInTheDocument();

    const link = within(listItem).getByRole("link", { name: "source" });
    expect(link).toHaveAttribute(
      "href",
      "https://world.openfoodfacts.org/api/v2/search?search_terms=Jacobs"
    );
    expect(link).toHaveAttribute(
      "title",
      "https://world.openfoodfacts.org/api/v2/search?search_terms=Jacobs"
    );
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noreferrer");

    // SG-118 discipline: raw source URL is not visible as text content
    expect(section.textContent).not.toContain("world.openfoodfacts.org");

    expect(within(listItem).getByText(/2026-09-25T00:00:00\+00:00/)).toBeInTheDocument();
  });

  test("falls back to 'Source not named' when source_type is omitted/undefined", () => {
    const alternates: WebAlternate[] = [
      {
        field: "model",
        value: "Model X",
        source_type: null,
        source_url: null,
        retrieved_at: null,
      },
    ];

    render(<WebAlternates alternates={alternates} />);

    const listItem = screen.getByTestId("web-alternate-model");
    // SG-301 G2: a missing source reads "Source not named", never "unknown source".
    expect(within(listItem).getByText("Source not named")).toBeInTheDocument();
    expect(within(listItem).queryByRole("link")).toBeNull();
  });

  test("renders multiple alternates", () => {
    const alternates: WebAlternate[] = [
      {
        field: "brand",
        value: "Brand A",
        source_type: "web:source1",
        source_url: null,
        retrieved_at: null,
      },
      {
        field: "category",
        value: "Electronics",
        source_type: "web:source2",
        source_url: null,
        retrieved_at: null,
      },
    ];

    render(<WebAlternates alternates={alternates} />);

    expect(screen.getByTestId("web-alternate-brand")).toBeInTheDocument();
    expect(screen.getByTestId("web-alternate-category")).toBeInTheDocument();
    expect(screen.getByText("Brand A")).toBeInTheDocument();
    expect(screen.getByText("Electronics")).toBeInTheDocument();
  });
});
