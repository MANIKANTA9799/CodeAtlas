import React, { useState } from "react";
import { SourceItem } from "./ContextPanel";
import { MarkdownBlock } from "./MarkdownBlock";

export interface Message {
    id: string;
    sender: "user" | "assistant";
    content: string;
    sources?: SourceItem[];
}

interface ChatPanelProps {
    onSourcesUpdate: (sources: any[]) => void;
    projectName: string;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ onSourcesUpdate, projectName }) => {
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

        // Create a placeholder assistant message that we will append tokens to
        const assistantId = (Date.now() + 1).toString();
        const initialAssistantMessage: Message = {
            id: assistantId,
            sender: "assistant",
            content: "",
            sources: [],
        };

        setMessages((prev) => [...prev, userMessage, initialAssistantMessage]);
        setInput("");
        setLoading(true);

        try {
            const response = await fetch("http://127.0.0.1:8000/api/v1/chat/stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: userMessage.content,
                    project_name: projectName // <-- Ensures we search the active bucket!
                }),
            });

            if (!response.ok || !response.body) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            setLoading(false); // Stop the "Thinking..." animation once the stream connects

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let done = false;

            while (!done) {
                const { value, done: readerDone } = await reader.read();
                done = readerDone;
                if (value) {
                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split("\n\n"); // SSE separates events by double newlines

                    for (const line of lines) {
                        if (line.startsWith("data: ")) {
                            const dataStr = line.replace("data: ", "");

                            if (dataStr === "[DONE]") {
                                break;
                            }

                            try {
                                const parsed = JSON.parse(dataStr);

                                // If the backend sends the sources first
                                if (parsed.type === "sources") {
                                    onSourcesUpdate(parsed.sources || []);
                                    setMessages((prev) =>
                                        prev.map((msg) =>
                                            msg.id === assistantId ? { ...msg, sources: parsed.sources } : msg
                                        )
                                    );
                                }
                                // If the backend sends a text token
                                else if (parsed.type === "token") {
                                    setMessages((prev) =>
                                        prev.map((msg) =>
                                            msg.id === assistantId ? { ...msg, content: msg.content + parsed.content } : msg
                                        )
                                    );
                                }
                            } catch (e) {
                                console.error("Error parsing stream chunk", e);
                            }
                        }
                    }
                }
            }
        } catch (error) {
            setLoading(false);
            setMessages((prev) => [
                ...prev,
                {
                    id: (Date.now() + 2).toString(),
                    sender: "assistant",
                    content: `Error executing query: ${error instanceof Error ? error.message : "Unknown error"}`,
                },
            ]);
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-950 text-gray-100">
            {/* The duplicate "CodeAtlas Workspace" header div has been completely removed from here */}

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
                                className={`max-w-3xl px-5 py-4 rounded-xl shadow-sm ${msg.sender === "user"
                                    ? "bg-blue-600 text-white rounded-br-none"
                                    : "bg-gray-900 border border-gray-800 text-gray-200 rounded-bl-none"
                                    }`}
                            >
                                {msg.sender === "user" ? (
                                    <div className="text-sm whitespace-pre-wrap leading-relaxed">
                                        {msg.content}
                                    </div>
                                ) : (
                                    <MarkdownBlock content={msg.content} />
                                )}
                            </div>
                        </div>
                    ))
                )}

                {loading && (
                    <div className="flex items-center space-x-2 text-gray-400 text-sm italic">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping" />
                        <span>Thinking...</span>
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