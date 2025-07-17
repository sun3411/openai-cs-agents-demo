"use client";

import { useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState<{ role: "user" | "bot"; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user" as const, content: input };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          conversation_id: conversationId || undefined,
        }),
      });
      const data = await res.json();
      setConversationId(data.conversation_id);
      setMessages((prev) => [...prev, { role: "bot", content: data.reply }]);
    } catch (e) {
      setMessages((prev) => [...prev, { role: "bot", content: "出错了，请稍后再试。" }]);
    }
    setInput("");
    setLoading(false);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
      <div className="w-full max-w-xl bg-white rounded shadow p-6 mt-10">
        <h1 className="text-2xl font-bold mb-4 text-center">财务智能问答机器人</h1>
        <div className="h-96 overflow-y-auto border rounded p-4 bg-gray-50 mb-4">
          {messages.length === 0 && (
            <div className="text-gray-400 text-center mt-20">请输入您的财务相关问题…</div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={`mb-3 flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`px-4 py-2 rounded-lg max-w-[80%] whitespace-pre-line ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-900"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="mb-3 flex justify-start">
              <div className="px-4 py-2 rounded-lg bg-gray-200 text-gray-900 animate-pulse">正在思考…</div>
            </div>
          )}
        </div>
        <div className="flex gap-2">
          <input
            className="flex-1 border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            type="text"
            placeholder="请输入问题，回车发送"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !loading) sendMessage();
            }}
            disabled={loading}
          />
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
            onClick={sendMessage}
            disabled={loading || !input.trim()}
          >
            发送
          </button>
        </div>
      </div>
    </div>
  );
}
