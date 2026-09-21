import type { ChatMessage } from "../api/types";

type Props = {
  messages: ChatMessage[];
};

export function ChatTranscript({ messages }: Props) {
  if (messages.length === 0) {
    return (
      <div role="status" className="text-muted-foreground" style={{ fontSize: 13 }}>
        No messages yet.
      </div>
    );
  }
  return (
    <ol style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 8 }}>
      {messages.map((message, index) => (
        <li
          key={index}
          className={`${message.role === "user" ? "bg-accent text-accent-foreground" : "bg-card-muted text-foreground"} border-border`}
          style={{
            padding: 10,
            borderRadius: 8,
            borderStyle: "solid",
            borderWidth: 1,
          }}
        >
          <div className="text-muted-foreground" style={{ fontSize: 11, textTransform: "uppercase" }}>
            {message.role}
          </div>
          <div style={{ whiteSpace: "pre-wrap" }}>{message.text}</div>
        </li>
      ))}
    </ol>
  );
}
