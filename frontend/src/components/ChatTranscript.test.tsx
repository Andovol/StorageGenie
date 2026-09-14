import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChatTranscript } from "./ChatTranscript";

describe("ChatTranscript", () => {
  test("shows an empty state when there are no messages", () => {
    render(<ChatTranscript messages={[]} />);
    expect(screen.getByRole("status")).toHaveTextContent("No messages yet.");
  });

  test("renders each message with its role and text", () => {
    render(
      <ChatTranscript
        messages={[
          { role: "user", text: "When does the milk expire?" },
          { role: "assistant", text: "Whole milk expires on 2026-09-16." },
        ]}
      />
    );
    expect(screen.getByText("When does the milk expire?")).toBeInTheDocument();
    expect(screen.getByText("Whole milk expires on 2026-09-16.")).toBeInTheDocument();
    expect(screen.getByText("user")).toBeInTheDocument();
    expect(screen.getByText("assistant")).toBeInTheDocument();
  });
});
