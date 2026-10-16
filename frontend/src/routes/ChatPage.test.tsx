import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { ChatPage } from "./ChatPage";
import { HouseholdProvider } from "../hooks/HouseholdContext";

const household = { id: "hh-chat", name: "Chat home", created_at: "2026-01-01" };

const api = vi.hoisted(() => ({
  sendChat: vi.fn(),
  logChatCorrection: vi.fn(),
}));
vi.mock("../api/client", () => api);
vi.mock("../hooks/useAssets", () => ({ useHouseholds: () => ({ data: [household] }) }));

function renderPage() {
  // SG-196: household selection now comes from the shared context provider;
  // preserved behavior: every request still carries hh-chat.
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <HouseholdProvider>
        <MemoryRouter>
          <ChatPage />
        </MemoryRouter>
      </HouseholdProvider>
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

  test("submitting the form by pressing Enter sends the question", async () => {
    api.sendChat.mockResolvedValue({
      status: "ok",
      answer: "Milk is in stock.",
      grounded: true,
      empty_catalogue: false,
      category: "food",
      catalogue_size: 1,
    });
    renderPage();

    const input = screen.getByLabelText("Question");
    fireEvent.change(input, { target: { value: "Is milk in stock?" } });
    fireEvent.submit(input);

    await waitFor(() =>
      expect(api.sendChat).toHaveBeenCalledWith("food", household.id, "Is milk in stock?")
    );
    expect(await screen.findByText("Milk is in stock.")).toBeInTheDocument();
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

  test("the disabled state links to Settings; the enabled path does not", async () => {
    api.sendChat.mockResolvedValue({
      status: "skipped",
      reason: "consent_disabled",
      answer: null,
      grounded: false,
      empty_catalogue: false,
      category: "food",
      catalogue_size: 1,
    });
    const { unmount } = renderPage();

    fireEvent.change(screen.getByLabelText("Question"), { target: { value: "Hello?" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    const link = await screen.findByRole("link", { name: "Enable AI in Settings to use chat" });
    expect(link.getAttribute("href") || "").toContain("/settings");
    expect(link).toHaveClass("text-link");
    unmount();

    api.sendChat.mockResolvedValue({
      status: "ok",
      answer: "Whole milk expires on 2026-09-16.",
      grounded: true,
      empty_catalogue: false,
      category: "food",
      catalogue_size: 1,
    });
    renderPage();
    fireEvent.change(screen.getByLabelText("Question"), { target: { value: "When?" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    await screen.findByText("Whole milk expires on 2026-09-16.");
    expect(
      screen.queryByRole("link", { name: "Enable AI in Settings to use chat" })
    ).not.toBeInTheDocument();
  });

  test("an empty catalogue with unclassified items names the cause and links to the Inbox", async () => {
    api.sendChat.mockResolvedValue({
      status: "ok",
      answer: "There is no catalogue data recorded for this category yet, so I cannot answer from your items.",
      grounded: true,
      empty_catalogue: true,
      category: "food",
      catalogue_size: 0,
      unclassified_count: 3,
    });
    renderPage();

    fireEvent.change(screen.getByLabelText("Question"), { target: { value: "What expires?" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("No catalogue data for this category yet.");
    expect(alert).toHaveTextContent("No classified items in Food yet — 3 awaiting classification.");
    const link = await screen.findByRole("link", { name: "Review them in the Inbox." });
    expect(link.getAttribute("href") || "").toContain("/inbox?household_id=hh-chat");
    expect(link).toHaveClass("text-link");
  });

  test("an empty catalogue with zero unclassified items keeps the legacy single line", async () => {
    api.sendChat.mockResolvedValue({
      status: "ok",
      answer: "There is no catalogue data recorded for this category yet, so I cannot answer from your items.",
      grounded: true,
      empty_catalogue: true,
      category: "food",
      catalogue_size: 0,
      unclassified_count: 0,
    });
    renderPage();

    fireEvent.change(screen.getByLabelText("Question"), { target: { value: "What expires?" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("No catalogue data for this category yet.");
    expect(alert).not.toHaveTextContent("awaiting classification");
    expect(screen.queryByRole("link", { name: "Review them in the Inbox." })).not.toBeInTheDocument();
  });

  test("an empty catalogue with the key absent keeps the legacy single line", async () => {
    api.sendChat.mockResolvedValue({
      status: "ok",
      answer: "There is no catalogue data recorded for this category yet, so I cannot answer from your items.",
      grounded: true,
      empty_catalogue: true,
      category: "food",
      catalogue_size: 0,
    });
    renderPage();

    fireEvent.change(screen.getByLabelText("Question"), { target: { value: "What expires?" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("No catalogue data for this category yet.");
    expect(alert).not.toHaveTextContent("awaiting classification");
    expect(screen.queryByRole("link", { name: "Review them in the Inbox." })).not.toBeInTheDocument();
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

  test("the household select carries the shared themed control treatment (SG-167 G1a)", () => {
    renderPage();

    const select = screen.getByRole("combobox", { name: /household/i });
    expect(select).toHaveClass("bg-background", "text-foreground", "border-border");
  });
});
