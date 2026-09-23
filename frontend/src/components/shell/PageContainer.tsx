import type { CSSProperties, ReactNode } from "react";

/**
 * SG-105 G1: one centered page container shared by every page. The single page
 * max-width lives here; the narrow form width is the container's `form` variant
 * so no page hand-rolls a `maxWidth`/padding pair.
 */
export const PAGE_MAX_WIDTH = 1100;
export const FORM_MAX_WIDTH = 520;
export const PAGE_CONTAINER_CLASS = "page-container";

export function pageContainerStyle(variant: "page" | "form" = "page"): CSSProperties {
  return {
    width: "100%",
    maxWidth: variant === "form" ? FORM_MAX_WIDTH : PAGE_MAX_WIDTH,
    marginLeft: "auto",
    marginRight: "auto",
    padding: 24,
  };
}

type PageContainerProps = {
  variant?: "page" | "form";
  as?: "div" | "main";
  className?: string;
  children: ReactNode;
};

export function PageContainer({
  variant = "page",
  as = "div",
  className,
  children,
}: PageContainerProps) {
  const Tag = as;
  return (
    <Tag
      data-testid={variant === "form" ? "form-container" : "page-container"}
      data-variant={variant}
      className={`${PAGE_CONTAINER_CLASS}${variant === "form" ? " page-container--form" : ""}${className ? ` ${className}` : ""}`}
      style={pageContainerStyle(variant)}
    >
      {children}
    </Tag>
  );
}
