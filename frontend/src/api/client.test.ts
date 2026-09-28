import { describe, test, expect, vi, beforeEach, afterEach } from "vitest";
import {
  buildUrl,
  apiGet,
  apiPatch,
  apiPut,
  apiPost,
  fetchAiSettings,
  updateAiModel,
  fetchPlanningSuggestions,
  candidateDecision,
  sendChat,
  runPlanning,
  resolveReviewTask,
} from "./client";

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

describe("apiPatch", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("sends PATCH request with correct method, headers, body, and params, and returns JSON response", async () => {
    const mockResponseBody = { id: "123", name: "Updated Asset" };
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: true,
        json: async () => mockResponseBody,
      })
    );

    const payload = { name: "Updated Asset" };
    const customHeaders = { "X-Custom-Header": "custom-value" };
    const result = await apiPatch<{ id: string; name: string }>(
      "/v1/assets/123",
      payload,
      { household_id: "h1" },
      customHeaders
    );

    expect(result).toEqual(mockResponseBody);
    expect(fetch).toHaveBeenCalledWith(
      buildUrl("/v1/assets/123", { household_id: "h1" }),
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-Custom-Header": "custom-value",
        },
        body: JSON.stringify(payload),
      }
    );
  });

  test("throws error with detail message on failed PATCH request", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: false,
        status: 400,
        statusText: "Bad Request",
        json: async () => ({ detail: "Cannot update asset" }),
      })
    );

    await expect(apiPatch("/v1/assets/123", { name: "New Name" })).rejects.toThrow(
      "Cannot update asset"
    );
  });

  test("falls back to status error string when body JSON parsing fails", async () => {
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

    await expect(apiPatch("/v1/assets/123", { name: "New Name" })).rejects.toThrow(
      "PATCH /v1/assets/123 failed: 500"
    );
  });
});

describe("apiPut", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("returns JSON response on success and sends correct options", async () => {
    const mockData = { id: "123", updated: true };
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: true,
        json: async () => mockData,
      })
    );

    const payload = { name: "Updated Item" };
    const result = await apiPut<{ id: string; updated: boolean }>(
      "/v1/items/123",
      payload,
      { lang: "en" },
      { "X-Custom": "Value" }
    );

    expect(result).toEqual(mockData);
    expect(fetch).toHaveBeenCalledWith(buildUrl("/v1/items/123", { lang: "en" }), {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-Custom": "Value",
      },
      body: JSON.stringify(payload),
    });
  });

  test("throws error with detail on failed request when detail string exists", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: false,
        status: 400,
        statusText: "Bad Request",
        json: async () => ({ detail: "Invalid field" }),
      })
    );

    await expect(apiPut("/v1/items/123", {})).rejects.toThrow("Invalid field");
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

    await expect(apiPut("/v1/items/123", {})).rejects.toThrow("PUT /v1/items/123 failed: 500");
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

describe("apiPost", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("returns JSON response on success and sends correct method, headers, params, and body", async () => {
    const mockData = { id: "456", name: "New Asset" };
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: true,
        json: async () => mockData,
      })
    );

    const body = { name: "New Asset" };
    const params = { household_id: "h1" };
    const headers = { "X-Custom-Header": "value" };

    const result = await apiPost<{ id: string; name: string }>("/v1/assets", body, params, headers);

    expect(result).toEqual(mockData);
    expect(fetch).toHaveBeenCalledWith(buildUrl("/v1/assets", params), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Custom-Header": "value",
      },
      body: JSON.stringify(body),
    });
  });

  test("throws error with detail on failed request when detail string exists", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: false,
        status: 400,
        statusText: "Bad Request",
        json: async () => ({ detail: "Invalid request body" }),
      })
    );

    await expect(apiPost("/v1/assets", { invalid: true })).rejects.toThrow("Invalid request body");
  });

  test("throws error with title and detail on failed RFC 9457 response", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: false,
        status: 422,
        statusText: "Unprocessable Entity",
        json: async () => ({ title: "Validation Error", detail: "field required" }),
      })
    );

    await expect(apiPost("/v1/assets", {})).rejects.toThrow("field required");
  });

  test("throws error with title only on failed RFC 9457 response without detail string", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: false,
        status: 400,
        statusText: "Bad Request",
        json: async () => ({ title: "Validation Failed", detail: null }),
      })
    );

    await expect(apiPost("/v1/assets", {})).rejects.toThrow("Validation Failed");
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

    await expect(apiPost("/v1/assets", {})).rejects.toThrow("Internal Server Error");
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

    await expect(apiPost("/v1/assets", {})).rejects.toThrow("POST /v1/assets failed: 500");
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

describe("apiPost helpers", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("candidateDecision sends POST to decision endpoint", async () => {
    const mockRes = { candidate_id: "c1", state: "accepted" };
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: true,
        json: async () => mockRes,
      })
    );

    const res = await candidateDecision("c1", "h1", "accept", { name: "New Name" });
    expect(res).toEqual(mockRes);
    expect(fetch).toHaveBeenCalledWith(
      buildUrl("/v1/candidates/c1/decision", { household_id: "h1" }),
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "accept", corrected_fields: { name: "New Name" } }),
      }
    );
  });

  test("sendChat sends POST to chat endpoint", async () => {
    const mockRes = { reply: "Hello!" };
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: true,
        json: async () => mockRes,
      })
    );

    const res = await sendChat("general", "h1", "hi");
    expect(res).toEqual(mockRes);
    expect(fetch).toHaveBeenCalledWith(
      buildUrl("/v1/chat/general", { household_id: "h1" }),
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "hi" }),
      }
    );
  });

  test("runPlanning sends POST to planning run endpoint", async () => {
    const mockRes = { status: "success" };
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: true,
        json: async () => mockRes,
      })
    );

    const res = await runPlanning("h1");
    expect(res).toEqual(mockRes);
    expect(fetch).toHaveBeenCalledWith(
      buildUrl("/v1/planning/run", { household_id: "h1" }),
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      }
    );
  });

  test("resolveReviewTask sends POST to resolve endpoint", async () => {
    const mockRes = { id: "t1", status: "resolved" };
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        ok: true,
        json: async () => mockRes,
      })
    );

    const res = await resolveReviewTask("t1", "h1");
    expect(res).toEqual(mockRes);
    expect(fetch).toHaveBeenCalledWith(
      buildUrl("/v1/review-tasks/t1/resolve", { household_id: "h1" }),
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      }
    );
  });
});
