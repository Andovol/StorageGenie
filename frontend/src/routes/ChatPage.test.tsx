import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ChatPage } from "./ChatPage";

const household = { id: "hh-chat", name: "Chat home", created_at: "2026-01-01" };

const api = vi.hoisted(() => ({
  sendChat: vi.fn(),
  logChatCorrection: vi.fn(),
}));
vi.mock("../api/client", () => api);
vi.mock("../hooks/useAssets", () => ({ useHouseholds: () => ({ data: [household] }) }));

function renderPage() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <ChatPage />
    </QueryClientProvider>
  );
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("ChatPage", () => {
  test("sending a question posts and renders the grounded reply", async () => {
    api.sendChat.mockResolvedValue({
      status: "ok",
      answer: "Whole milk expires on 2026-09-16.",
      grounded: true,
      empty_catalogue: false,
      category: "food",
      catalogue_size: 1,
    });
    renderPage();

    fireEvent.change(screen.getByLabelText("Question"), {
      target: { value: "When does the milk expire?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() =>
      expect(api.sendChat).toHaveBeenCalledWith("food", household.id, "When does the milk expire?")
    );
    expect(await screen.findByText("Whole milk expires on 2026-09-16.")).toBeInTheDocument();
  });

  test("the category selection drives the request", async () => {
    api.sendChat.mockResolvedValue({
      status: "ok",
      answer: "No tablets are recorded.",
      grounded: true,
      empty_catalogue: false,
      category: "medicine",
      catalogue_size: 0,
    });
    renderPage();

    fireEvent.change(screen.getByLabelText("Category"), { target: { value: "medicine" } });
    fireEvent.change(screen.getByLabelText("Question"), { target: { value: "Any tablets?" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() =>
      expect(api.sendChat).toHaveBeenCalledWith("medicine", household.id, "Any tablets?")
    );
  });

  test("logging a correction posts the explicit action", async () => {
    api.logChatCorrection.mockResolvedValue({
      id: "evt-1",
      kind: "correction",
      category: "food",
      message: "the milk is open",
      created_at: null,
    });
    renderPage();

    fireEvent.change(screen.getByLabelText("Correction"), {
      target: { value: "the milk is open" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Log correction" }));

    await waitFor(() =>
      expect(api.logChatCorrection).toHaveBeenCalledWith("food", household.id, "the milk is open")
    );
    expect(await screen.findByRole("alert")).toHaveTextContent("Correction logged.");
  });

  test("a skipped call surfaces the refusal reason", async () => {
    api.sendChat.mockResolvedValue({
      status: "skipped",
      reason: "consent_disabled",
      answer: null,
      grounded: false,
      empty_catalogue: false,
      category: "food",
      catalogue_size: 1,
    });
    renderPage();

    fireEvent.change(screen.getByLabelText("Question"), { target: { value: "Hello?" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Chat did not run: consent_disabled"
    );
  });

  test("an unsupported category error surfaces", async () => {
    api.sendChat.mockRejectedValue(new Error("unknown chat category: snacks"));
    renderPage();

    fireEvent.change(screen.getByLabelText("Question"), { target: { value: "anything" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "unknown chat category: snacks"
    );
  });
});
