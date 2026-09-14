import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SettingsPage } from "./SettingsPage";

const api = vi.hoisted(() => ({
  fetchAiSettings: vi.fn(),
  updateAiModel: vi.fn(),
}));
vi.mock("../api/client", () => api);

const settings = {
  provider_id: "fake",
  model_id: "deepseek-v4-flash-vision-exp",
  allowed_model_ids: ["deepseek-v4-flash-vision-exp", "vision-second-model"],
  consent: false,
  per_job_cap: null,
  monthly_cap: null,
  prompt_category: "food",
};

function renderPage() {
  return render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <SettingsPage />
    </QueryClientProvider>
  );
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("SettingsPage model picker", () => {
  test("renders the endpoint's allowed list and the effective model", async () => {
    api.fetchAiSettings.mockResolvedValue(settings);
    renderPage();
    const select = (await screen.findByLabelText("AI model")) as HTMLSelectElement;
    await screen.findByRole("option", { name: settings.model_id });
    const optionValues = Array.from(select.querySelectorAll("option")).map((option) => option.value);
    expect(optionValues).toEqual(settings.allowed_model_ids);
    expect(select.value).toBe(settings.model_id);
  });

  test("selection PUTs the chosen model and refetches from the backend", async () => {
    api.fetchAiSettings
      .mockResolvedValueOnce(settings)
      .mockResolvedValue({ ...settings, model_id: "vision-second-model" });
    api.updateAiModel.mockResolvedValue({ ...settings, model_id: "vision-second-model" });
    renderPage();
    const select = (await screen.findByLabelText("AI model")) as HTMLSelectElement;
    await screen.findByRole("option", { name: "vision-second-model" });
    fireEvent.change(select, { target: { value: "vision-second-model" } });
    await waitFor(() => expect(api.updateAiModel).toHaveBeenCalledWith("vision-second-model"));
    await waitFor(() => expect(api.fetchAiSettings).toHaveBeenCalledTimes(2));
    await waitFor(() =>
      expect((screen.getByLabelText("AI model") as HTMLSelectElement).value).toBe(
        "vision-second-model"
      )
    );
  });

  test("a rejected selection surfaces the backend error", async () => {
    api.fetchAiSettings.mockResolvedValue(settings);
    api.updateAiModel.mockRejectedValue(new Error("unsupported model id: deepseek-v4-flash"));
    renderPage();
    const select = (await screen.findByLabelText("AI model")) as HTMLSelectElement;
    await screen.findByRole("option", { name: "vision-second-model" });
    fireEvent.change(select, { target: { value: "vision-second-model" } });
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "unsupported model id: deepseek-v4-flash"
    );
  });
});
