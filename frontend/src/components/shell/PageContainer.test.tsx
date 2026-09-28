import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import {
  FORM_MAX_WIDTH,
  PAGE_MAX_WIDTH,
  PAGE_CONTAINER_CLASS,
  PageContainer,
  pageContainerStyle,
} from "./PageContainer";

describe("pageContainerStyle", () => {
  test("returns default style for page variant when no argument is provided", () => {
    const style = pageContainerStyle();
    expect(style).toEqual({
      width: "100%",
      maxWidth: PAGE_MAX_WIDTH,
      marginLeft: "auto",
      marginRight: "auto",
      padding: 24,
    });
  });

  test("returns style for explicit page variant", () => {
    const style = pageContainerStyle("page");
    expect(style).toEqual({
      width: "100%",
      maxWidth: PAGE_MAX_WIDTH,
      marginLeft: "auto",
      marginRight: "auto",
      padding: 24,
    });
  });

  test("returns style for form variant with form max width", () => {
    const style = pageContainerStyle("form");
    expect(style).toEqual({
      width: "100%",
      maxWidth: FORM_MAX_WIDTH,
      marginLeft: "auto",
      marginRight: "auto",
      padding: 24,
    });
  });
});

describe("PageContainer component", () => {
  test("renders default page container div element with children and default page styles", () => {
    render(<PageContainer>Test Content</PageContainer>);
    const container = screen.getByTestId("page-container");

    expect(container).toBeInTheDocument();
    expect(container.tagName).toBe("DIV");
    expect(container).toHaveAttribute("data-variant", "page");
    expect(container).toHaveClass(PAGE_CONTAINER_CLASS);
    expect(container).toHaveStyle({
      width: "100%",
      maxWidth: `${PAGE_MAX_WIDTH}px`,
      marginLeft: "auto",
      marginRight: "auto",
      padding: "24px",
    });
    expect(container).toHaveTextContent("Test Content");
  });

  test("renders form variant container with form styles and class modifier", () => {
    render(<PageContainer variant="form">Form Content</PageContainer>);
    const container = screen.getByTestId("form-container");

    expect(container).toBeInTheDocument();
    expect(container).toHaveAttribute("data-variant", "form");
    expect(container).toHaveClass(PAGE_CONTAINER_CLASS);
    expect(container).toHaveClass("page-container--form");
    expect(container).toHaveStyle({
      maxWidth: `${FORM_MAX_WIDTH}px`,
    });
  });

  test("renders custom tag element and handles custom className", () => {
    render(
      <PageContainer as="main" className="custom-class">
        Main Content
      </PageContainer>
    );
    const container = screen.getByTestId("page-container");

    expect(container.tagName).toBe("MAIN");
    expect(container).toHaveClass(PAGE_CONTAINER_CLASS);
    expect(container).toHaveClass("custom-class");
  });
});
