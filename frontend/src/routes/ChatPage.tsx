import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { logChatCorrection, sendChat } from "../api/client";
import type { ChatMessage, ChatResponse, Household } from "../api/types";
import { ChatTranscript } from "../components/ChatTranscript";
import { useHouseholds } from "../hooks/useAssets";

const CATEGORIES = [
  { value: "food", label: "Food" },
  { value: "medicine", label: "Medicine" },
] as const;

export function ChatPage() {
  const { data: households } = useHouseholds();
  const [householdId, setHouseholdId] = useState(
    () => localStorage.getItem("household_id") || ""
  );
  const [category, setCategory] = useState("food");
  const [input, setInput] = useState("");
  const [correction, setCorrection] = useState("");
  const [transcript, setTranscript] = useState<ChatMessage[]>([]);
  const [notice, setNotice] = useState("");
  const effectiveHousehold = householdId || households?.[0]?.id || "";

  useEffect(() => {
    if (!householdId && households?.[0]) {
      setHouseholdId(households[0].id);
      localStorage.setItem("household_id", households[0].id);
    }
  }, [householdId, households]);

  const send = useMutation({
    mutationFn: () => sendChat(category, effectiveHousehold, input),
    onSuccess: (result: ChatResponse) => {
      if (result.status === "skipped") {
        setNotice(`Chat did not run: ${result.reason ?? "skipped"}`);
        setTranscript((messages) => [
          ...messages,
          { role: "user", text: input },
          { role: "assistant", text: `(no answer: ${result.reason ?? "skipped"})` },
        ]);
      } else if (result.status !== "ok") {
        setNotice(`Chat failed: ${result.reason ?? result.status}`);
      } else {
        setNotice(
          result.empty_catalogue ? "No catalogue data for this category yet." : ""
        );
        setTranscript((messages) => [
          ...messages,
          { role: "user", text: input },
          { role: "assistant", text: result.answer ?? "" },
        ]);
      }
      setInput("");
    },
    onError: (error: unknown) => setNotice(String(error)),
  });

  const logCorrection = useMutation({
    mutationFn: () => logChatCorrection(category, effectiveHousehold, correction),
    onSuccess: () => {
      setNotice("Correction logged.");
      setCorrection("");
    },
    onError: (error: unknown) => setNotice(String(error)),
  });

  return (
    <div style={{ padding: 24, maxWidth: 900 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Chat</h1>
        <label>
          Household{" "}
          <select
            value={effectiveHousehold}
            onChange={(event) => {
              setHouseholdId(event.target.value);
              localStorage.setItem("household_id", event.target.value);
            }}
          >
            <option value="">Select household</option>
            {(households as Household[] | undefined)?.map((household) => (
              <option key={household.id} value={household.id}>
                {household.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      <p style={{ color: "#6b7280", fontSize: 13 }}>
        Answers are grounded in the selected category&apos;s catalogue only. Chat changes no
        asset, job or setting, and sends nothing on a schedule.
      </p>

      <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 12 }}>
        <label>
          Category{" "}
          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
          >
            {CATEGORIES.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      {notice && (
        <div role="alert" style={{ marginTop: 12, color: "#374151" }}>
          {notice}
        </div>
      )}

      <section style={{ marginTop: 16 }}>
        <ChatTranscript messages={transcript} />
      </section>

      <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <input
          aria-label="Question"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask about this category…"
          style={{ flex: 1, padding: 8 }}
        />
        <button
          type="button"
          onClick={() => send.mutate()}
          disabled={!effectiveHousehold || !input.trim() || send.isPending}
        >
          {send.isPending ? "Sending…" : "Send"}
        </button>
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <input
          aria-label="Correction"
          value={correction}
          onChange={(event) => setCorrection(event.target.value)}
          placeholder="Log a correction…"
          style={{ flex: 1, padding: 8 }}
        />
        <button
          type="button"
          onClick={() => logCorrection.mutate()}
          disabled={!effectiveHousehold || !correction.trim() || logCorrection.isPending}
        >
          Log correction
        </button>
      </div>
    </div>
  );
}
