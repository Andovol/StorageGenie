import { describe, expect, test } from "vitest";
import { formatJobDate, labelExpiryState, labelStepName } from "./labels";

const BACKEND_STEPS = [
  "EXTRACTING_DETERMINISTIC_SIGNALS",
  "NORMALIZING",
  "DEDUPLICATING",
  "COMMITTING",
  "AWAITING_REVIEW",
];

describe("SG-312 step names in plain words (I3)", () => {
  test("the five backend steps read as sentence-case owner words", () => {
    expect(labelStepName("EXTRACTING_DETERMINISTIC_SIGNALS")).toBe("Checking the file");
    expect(labelStepName("NORMALIZING")).toBe("Tidying the details");
    expect(labelStepName("DEDUPLICATING")).toBe("Looking for duplicates");
    expect(labelStepName("COMMITTING")).toBe("Saving");
    expect(labelStepName("AWAITING_REVIEW")).toBe("Your review");
  });
  test("no backend step keeps an uppercase word or an underscore", () => {
    for (const raw of BACKEND_STEPS) {
      expect(labelStepName(raw)).not.toMatch(/[A-Z]{3,}|_/);
    }
  });
  test("an unmapped step reads as sentence case, never raw", () => {
    expect(labelStepName("SOME_NEW_STEP")).toBe("Some new step");
  });
});

describe("SG-312 job date in plain words (I3)", () => {
  const now = new Date(2026, 10, 12, 9, 0);
  test("a past date reads day, short month and time", () => {
    expect(formatJobDate(new Date(2020, 2, 5, 14, 42).toISOString(), now)).toBe("5 Mar, 14:42");
  });
  test("a date from today reads Today and time", () => {
    expect(formatJobDate(new Date(2026, 10, 12, 14, 42).toISOString(), now)).toBe("Today, 14:42");
  });
  test("an empty or unreadable date reads nothing, never the raw value", () => {
    expect(formatJobDate(null, now)).toBe("");
    expect(formatJobDate("not a date", now)).toBe("");
  });
});

describe("SG-312 expiry state in plain words (I5)", () => {
  test("accepted reads Date confirmed", () => {
    expect(labelExpiryState("accepted")).toBe("Date confirmed");
  });
  test("proposed reads Date to confirm", () => {
    expect(labelExpiryState("proposed")).toBe("Date to confirm");
  });
  test("needs_evidence reads Needs a date", () => {
    expect(labelExpiryState("needs_evidence")).toBe("Needs a date");
  });
  test("No date stays No date", () => {
    expect(labelExpiryState("No date")).toBe("No date");
  });
});
