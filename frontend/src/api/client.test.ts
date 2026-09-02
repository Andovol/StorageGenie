import { describe, test, expect } from "vitest";
import { buildUrl } from "./client";

describe("buildUrl", () => {
  test("injects household_id", () => {
    expect(buildUrl("/v1/assets", { household_id: "h1" })).toContain("household_id=h1");
  });
  test("omits empty params", () => {
    const url = buildUrl("/v1/assets", { household_id: "h1", q: "" });
    expect(url).not.toContain("q=");
  });
  test("builds full url with BASE", () => {
    const url = buildUrl("/v1/assets", { household_id: "h1" });
    expect(url).toContain("/v1/assets");
  });
});
