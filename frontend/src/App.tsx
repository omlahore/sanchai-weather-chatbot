import React, { useState, useCallback, FormEvent, KeyboardEvent } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

const containerStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  height: "100vh",
  maxWidth: "800px",
  margin: "0 auto",
  padding: "16px",
  boxSizing: "border-box",
};

const chatBoxStyle: React.CSSProperties = {
  flex: 1,
  overflowY: "auto",
  border: "1px solid #ddd",
  borderRadius: "8px",
  padding: "12px",
  marginBottom: "12px",
  backgroundColor: "#fafafa",
};

const inputRowStyle: React.CSSProperties = {
  display: "flex",
  gap: "8px",
};

const inputStyle: React.CSSProperties = {
  flex: 1,
  padding: "8px 10px",
  borderRadius: "6px",
  border: "1px solid #ccc",
  fontSize: "14px",
};

const buttonStyle: React.CSSProperties = {
  padding: "8px 16px",
  borderRadius: "6px",
  border: "none",
  backgroundColor: "#2563eb",
  color: "#fff",
  fontSize: "14px",
  cursor: "pointer",
};

const messageBubbleBase: React.CSSProperties = {
  padding: "8px 10px",
  borderRadius: "8px",
  marginBottom: "6px",
  maxWidth: "100%",
  whiteSpace: "pre-wrap",
};

const userBubble: React.CSSProperties = {
  ...messageBubbleBase,
  alignSelf: "flex-end",
  backgroundColor: "#e0f2fe",
};

const assistantBubble: React.CSSProperties = {
  ...messageBubbleBase,
  alignSelf: "flex-start",
  backgroundColor: "#e5e7eb",
};

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const newUserMessage: Message = { role: "user", content: trimmed };
    setMessages((prev) => [...prev, newUserMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const resp = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: trimmed }),
      });

      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(text || `Request failed with status ${resp.status}`);
      }

      const data: { answer?: string } = await resp.json();
      const answer = data.answer ?? "(No answer returned from backend)";

      const assistantMessage: Message = {
        role: "assistant",
        content: answer,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const assistantMessage: Message = {
        role: "assistant",
        content:
          "Sorry, something went wrong talking to the backend: " +
          (err?.message || String(err)),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    void sendMessage();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void sendMessage();
    }
  };

  return (
    <div style={containerStyle}>
      <h1 style={{ marginBottom: "8px" }}>SanchAI Weather</h1>
      <p style={{ marginTop: 0, marginBottom: "12px", fontSize: "14px", color: "#4b5563" }}>
        Ask anything, especially about the weather in any city. Weather answers use a real API.
      </p>

      <div style={chatBoxStyle}>
        {messages.length === 0 && (
          <div style={{ color: "#6b7280", fontSize: "14px" }}>
            Start by asking: &quot;What is the weather of Pune?&quot;
          </div>
        )}
        <div style={{ display: "flex", flexDirection: "column" }}>
          {messages.map((m, idx) => (
            <div
              key={idx}
              style={m.role === "user" ? userBubble : assistantBubble}
            >
              <strong style={{ display: "block", marginBottom: 2 }}>
                {m.role === "user" ? "You" : "Assistant"}
              </strong>
              <span>{m.content}</span>
            </div>
          ))}
          {isLoading && (
            <div style={assistantBubble}>
              <strong style={{ display: "block", marginBottom: 2 }}>Assistant</strong>
              <span>Thinking…</span>
            </div>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit} style={inputRowStyle}>
        <input
          type="text"
          placeholder="Type your message…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          style={inputStyle}
          disabled={isLoading}
        />
        <button
          type="submit"
          style={{
            ...buttonStyle,
            opacity: isLoading || !input.trim() ? 0.7 : 1,
          }}
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? "Sending…" : "Send"}
        </button>
      </form>
    </div>
  );
};

export default App;


