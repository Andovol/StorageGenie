import type { ChatMessage } from "../api/types";

type Props = {
  messages: ChatMessage[];
};

export function ChatTranscript({ messages }: Props) {
  if (messages.length === 0) {
    return (
      <div role="status" style={{ color: "#6b7280", fontSize: 13 }}>
        No messages yet.
      </div>
    );
  }
  return (
    <ol style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 8 }}>
      {messages.map((message, index) => (
        <li
          key={index}
          style={{
            padding: 10,
            borderRadius: 8,
            background: message.role === "user" ? "#eef2ff" : "#f9fafb",
            border: "1px solid #e5e7eb",
          }}
        >
          <div style={{ fontSize: 11, color: "#6b7280", textTransform: "uppercase" }}>
            {message.role}
          </div>
          <div style={{ whiteSpace: "pre-wrap" }}>{message.text}</div>
        </li>
      ))}
    </ol>
  );
}
