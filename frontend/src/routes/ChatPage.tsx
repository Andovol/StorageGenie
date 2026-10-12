import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { logChatCorrection, sendChat } from "../api/client";
import type { ChatMessage, ChatResponse, Household } from "../api/types";
import { ChatTranscript } from "../components/ChatTranscript";
import { HouseholdSelector } from "../components/HouseholdSelector";
import { PageContainer } from "../components/shell/PageContainer";
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
  const [aiDisabled, setAiDisabled] = useState(false);
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
        setAiDisabled(result.reason === "consent_disabled");
        setTranscript((messages) => [
          ...messages,
          { role: "user", text: input },
          { role: "assistant", text: `(no answer: ${result.reason ?? "skipped"})` },
        ]);
      } else if (result.status !== "ok") {
        setNotice(`Chat failed: ${result.reason ?? result.status}`);
        setAiDisabled(false);
      } else {
        setAiDisabled(false);
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
    <PageContainer className="text-foreground">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1 className="page-header text-foreground">Chat</h1>
        <HouseholdSelector
          value={effectiveHousehold}
          onChange={(id) => {
            setHouseholdId(id);
            localStorage.setItem("household_id", id);
          }}
          households={households as Household[] | undefined}
        />
      </div>

      <p className="text-muted-foreground" style={{ fontSize: 13 }}>
        Answers are grounded in the selected category&apos;s catalogue only. Chat changes no
        asset, job or setting, and sends nothing on a schedule.
      </p>

      <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 12 }}>
        <label>
          Category{" "}
          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="bg-background text-foreground border-border focus-ring"
            style={{ padding: "4px 8px", borderRadius: 6, borderStyle: "solid", borderWidth: 1 }}
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
        <div role="alert" className="text-foreground" style={{ marginTop: 12 }}>
          {notice}
          {aiDisabled && (
            <div style={{ marginTop: 4 }}>
              <Link to="/settings" className="text-link focus-ring">Enable AI in Settings to use chat</Link>
            </div>
          )}
        </div>
      )}

      <section style={{ marginTop: 16 }}>
        <ChatTranscript messages={transcript} />
      </section>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          if (effectiveHousehold && input.trim() && !send.isPending) {
            send.mutate();
          }
        }}
        style={{ display: "flex", gap: 8, marginTop: 16 }}
      >
        <input
          aria-label="Question"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask about this category…"
          className="bg-background text-foreground border-border focus-ring"
          style={{ flex: 1, padding: 8, borderRadius: 6, borderStyle: "solid", borderWidth: 1 }}
        />
        <button
          type="submit"
          disabled={!effectiveHousehold || !input.trim() || send.isPending}
          className="bg-primary text-primary-foreground focus-ring"
          style={{
            padding: "8px 16px",
            borderRadius: 6,
            border: "none",
            fontWeight: 600,
            cursor: !effectiveHousehold || !input.trim() || send.isPending ? "not-allowed" : "pointer",
          }}
        >
          {send.isPending ? "Sending…" : "Send"}
        </button>
      </form>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          if (effectiveHousehold && correction.trim() && !logCorrection.isPending) {
            logCorrection.mutate();
          }
        }}
        style={{ display: "flex", gap: 8, marginTop: 12 }}
      >
        <input
          aria-label="Correction"
          value={correction}
          onChange={(event) => setCorrection(event.target.value)}
          placeholder="Log a correction…"
          className="bg-background text-foreground border-border focus-ring"
          style={{ flex: 1, padding: 8, borderRadius: 6, borderStyle: "solid", borderWidth: 1 }}
        />
        <button
          type="submit"
          disabled={!effectiveHousehold || !correction.trim() || logCorrection.isPending}
          className="bg-card text-foreground border-border focus-ring"
          style={{
            padding: "8px 16px",
            borderRadius: 6,
            borderStyle: "solid",
            borderWidth: 1,
            cursor: !effectiveHousehold || !correction.trim() || logCorrection.isPending ? "not-allowed" : "pointer",
          }}
        >
          Log correction
        </button>
      </form>
    </PageContainer>
  );
}
