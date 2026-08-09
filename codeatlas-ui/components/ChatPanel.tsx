import React, { useState } from "react";
import { SourceItem } from "./ContextPanel";

export interface Message {
    id: string;
    sender: "user" | "assistant";
    content: string;
    sources?: SourceItem[];
}

interface ChatPanelProps {
    onSourcesUpdate: (sources: SourceItem[]) => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ onSourcesUpdate }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            sender: "user",
            content: input,
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setLoading(true);

        try {
            const response = await fetch("http://127.0.0.1:8000/api/v1/chat/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: userMessage.content }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            const data = await response.json();

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                sender: "assistant",
                content: data.answer,
                sources: data.sources || [],
            };

            setMessages((prev) => [...prev, assistantMessage]);
            onSourcesUpdate(data.sources || []);
        } catch (error) {
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                sender: "assistant",
                content: `Error executing query: ${error instanceof Error ? error.message : "Unknown error"}`,
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-950 text-gray-100">
            <div className="p-4 border-b border-gray-800 flex items-center justify-between">
                <h1 className="text-lg font-bold text-gray-100">CodeAtlas Workspace</h1>
                <span className="text-xs text-green-400 bg-green-950 border border-green-800 px-2.5 py-1 rounded-full">
                    Agent Online
                </span>
            </div>

            <div className="flex-1 p-4 overflow-y-auto space-y-4">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
                        <p className="font-semibold text-gray-400">Welcome to CodeAtlas</p>
                        <p className="text-xs mt-1">Ask questions regarding codebase structure or Git revision history.</p>
                    </div>
                ) : (
                    messages.map((msg) => (
                        <div
                            key={msg.id}
                            className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"
                                }`}
                        >
                            <div
                                className={`max-w-2xl px-4 py-3 rounded-xl text-sm whitespace-pre-wrap leading-relaxed ${msg.sender === "user"
                                        ? "bg-blue-600 text-white rounded-br-none"
                                        : "bg-gray-900 border border-gray-800 text-gray-200 rounded-bl-none"
                                    }`}
                            >
                                {msg.content}
                            </div>
                        </div>
                    ))
                )}

                {loading && (
                    <div className="flex items-center space-x-2 text-gray-400 text-xs italic">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping" />
                        <span>Analyzing AST structures and vector database...</span>
                    </div>
                )}
            </div>

            <div className="p-4 border-t border-gray-800 bg-gray-900">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSend()}
                        placeholder="Ask a query (e.g., How does AST chunking work?)"
                        className="flex-1 bg-gray-950 border border-gray-800 rounded-lg px-4 py-2.5 text-sm text-gray-100 focus:outline-none focus:border-blue-500"
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading}
                        className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 text-white text-sm font-medium px-5 py-2.5 rounded-lg transition-colors"
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
};