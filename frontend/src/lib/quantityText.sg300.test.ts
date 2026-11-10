import { describe, expect, test } from "vitest";
import { quantityLeftText } from "./quantityText";

describe("quantityLeftText (SG-300 shared formatter)", () => {
  test.each([
    [1, "pcs", true, "1 left"],
    [4, "", true, "4 left"],
    [2, "bottles", true, "2 left"],
    [340, "g", false, "340 g left"],
    [1, "kg", false, "1 kg left"],
    [null, "", true, "No count yet"],
    [null, "g", false, "No amount yet"],
  ])("quantity %s unit %j counted %s reads %s", (quantity, unit, counted, expected) => {
    expect(quantityLeftText(quantity as number | null, unit as string, counted)).toBe(expected);
  });

  test("no formatter output ever contains pcs", () => {
    expect(quantityLeftText(1, "pcs", true)).not.toContain("pcs");
  });
});
