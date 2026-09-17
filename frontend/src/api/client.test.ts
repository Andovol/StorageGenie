import { describe, test, expect, vi, beforeEach, afterEach } from "vitest";
import { buildUrl, apiGet, fetchAiSettings, updateAiModel, fetchPlanningSuggestions } from "./client";

function mockResponse(partial: Partial<Response>): Response {
  return partial as Response;
}

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

describe("apiGet", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("returns JSON response on success", async () => {
    const mockData = { id: "123", name: "Test Asset" };
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: true,
        json: async () => mockData,
      })
    );

    const result = await apiGet<{ id: string; name: string }>("/v1/assets", { household_id: "h1" });
    expect(result).toEqual(mockData);
    expect(fetch).toHaveBeenCalledWith(buildUrl("/v1/assets", { household_id: "h1" }));
  });

  test("throws error with detail on failed request when detail string exists", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: false,
        status: 404,
        statusText: "Not Found",
        json: async () => ({ detail: "Asset not found" }),
      })
    );

    await expect(apiGet("/v1/assets/999")).rejects.toThrow("Asset not found");
  });

  test("throws error with title and detail on failed RFC 9457 response", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: false,
        status: 400,
        statusText: "Bad Request",
        json: async () => ({ title: "Invalid Input", detail: "household_id is required" }),
      })
    );

    await expect(apiGet("/v1/assets")).rejects.toThrow("household_id is required");
  });

  test("throws error with title only on failed RFC 9457 response without detail string", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: false,
        status: 400,
        statusText: "Bad Request",
        json: async () => ({ title: "Invalid Input", detail: null }),
      })
    );

    await expect(apiGet("/v1/assets")).rejects.toThrow("Invalid Input");
  });

  test("falls back to statusText when body JSON parsing fails", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: false,
        status: 500,
        statusText: "Internal Server Error",
        json: async () => {
          throw new Error("Invalid JSON");
        },
      })
    );

    await expect(apiGet("/v1/assets")).rejects.toThrow("Internal Server Error");
  });

  test("falls back to status error string when body parsing fails and statusText is empty", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: false,
        status: 500,
        statusText: "",
        json: async () => {
          throw new Error("Invalid JSON");
        },
      })
    );

    await expect(apiGet("/v1/assets")).rejects.toThrow("GET /v1/assets failed: 500");
  });
});

describe("fetchAiSettings", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("fetches AI settings from endpoint", async () => {
    const mockSettings = { provider: "openai", model_id: "gpt-4" };
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: true,
        json: async () => mockSettings,
      })
    );

    const res = await fetchAiSettings();
    expect(res).toEqual(mockSettings);
    expect(fetch).toHaveBeenCalledWith(buildUrl("/v1/settings/ai", {}));
  });

  test("throws error when fetching AI settings fails", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: false,
        status: 500,
        statusText: "Internal Server Error",
        json: async () => ({ detail: "Failed to load AI settings" }),
      })
    );

    await expect(fetchAiSettings()).rejects.toThrow("Failed to load AI settings");
  });
});

describe("updateAiModel", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("updates AI model via PUT request", async () => {
    const updatedSettings = { provider: "openai", model_id: "gpt-4o" };
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: true,
        json: async () => updatedSettings,
      })
    );

    const res = await updateAiModel("gpt-4o");
    expect(res).toEqual(updatedSettings);
    expect(fetch).toHaveBeenCalledWith(buildUrl("/v1/settings/ai", {}), {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: "gpt-4o" }),
    });
  });

  test("throws error when updating AI model fails", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: false,
        status: 400,
        statusText: "Bad Request",
        json: async () => ({ detail: "Unsupported model_id" }),
      })
    );

    await expect(updateAiModel("invalid-model")).rejects.toThrow("Unsupported model_id");
  });
});

describe("fetchPlanningSuggestions", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("fetches planning suggestions with household_id and optional status filter", async () => {
    const mockSuggestions = { items: [], total: 0 };
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: true,
        json: async () => mockSuggestions,
      })
    );

    const res = await fetchPlanningSuggestions("h1", "pending");
    expect(res).toEqual(mockSuggestions);
    expect(fetch).toHaveBeenCalledWith(buildUrl("/v1/planning/suggestions", { household_id: "h1", status: "pending" }));
  });
});
