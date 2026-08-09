import React, { useState } from "react";

interface IngestionHeaderProps {
    onIngestionComplete: (path: string) => void;
}

export const IngestionHeader: React.FC<IngestionHeaderProps> = ({ onIngestionComplete }) => {
    const [repoPath, setRepoPath] = useState("");
    const [status, setStatus] = useState<"idle" | "code" | "git" | "success" | "error">("idle");
    const [errorMessage, setErrorMessage] = useState("");
    const [elapsedTime, setElapsedTime] = useState<number | null>(null);

    const handleIngest = async () => {
        if (!repoPath.trim()) return;

        setStatus("code");
        setErrorMessage("");
        setElapsedTime(null);
        const startTime = Date.now();

        try {
            // 1. Trigger Code AST Ingestion
            const codeRes = await fetch("http://127.0.0.1:8000/api/v1/ingest/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ repo_path: repoPath.trim() }),
            });

            if (!codeRes.ok) {
                const errorData = await codeRes.json();
                throw new Error(errorData.detail || "Code ingestion failed");
            }

            // 2. Trigger Git History Ingestion
            setStatus("git");
            const gitRes = await fetch("http://127.0.0.1:8000/api/v1/ingest/git", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ repo_path: repoPath.trim() }),
            });

            if (!gitRes.ok) {
                const errorData = await gitRes.json();
                throw new Error(errorData.detail || "Git history ingestion failed");
            }

            const totalSeconds = ((Date.now() - startTime) / 1000).toFixed(1);
            setElapsedTime(Number(totalSeconds));
            setStatus("success");
            onIngestionComplete(repoPath.trim());
        } catch (err) {
            setStatus("error");
            setErrorMessage(err instanceof Error ? err.message : "Ingestion failed");
        }
    };

    return (
        <header className="w-full bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between">
            <div className="flex items-center space-x-3">
                <span className="font-bold text-gray-100 text-lg tracking-wide">CodeAtlas</span>
                <span className="text-xs bg-blue-950 text-blue-400 border border-blue-800 px-2 py-0.5 rounded">
                    Local Engine
                </span>
            </div>

            <div className="flex items-center space-x-3 flex-1 max-w-2xl mx-8">
                <input
                    type="text"
                    value={repoPath}
                    onChange={(e) => setRepoPath(e.target.value)}
                    placeholder="Enter absolute repo path (e.g., C:/Users/name/projects/my-app)"
                    className="flex-1 bg-gray-950 border border-gray-800 rounded-lg px-4 py-1.5 text-sm text-gray-200 focus:outline-none focus:border-blue-500 font-mono"
                />
                <button
                    onClick={handleIngest}
                    disabled={status === "code" || status === "git"}
                    className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 text-white text-sm font-medium px-4 py-1.5 rounded-lg transition-colors whitespace-nowrap"
                >
                    {status === "code" && "Indexing AST..."}
                    {status === "git" && "Indexing Git..."}
                    {status !== "code" && status !== "git" && "Ingest Project"}
                </button>
            </div>

            <div className="flex items-center text-xs">
                {status === "idle" && (
                    <span className="text-gray-500">No project ingested</span>
                )}
                {status === "success" && (
                    <span className="text-green-400 font-medium">
                        Indexed in {elapsedTime}s
                    </span>
                )}
                {status === "error" && (
                    <span className="text-red-400 font-medium truncate max-w-xs" title={errorMessage}>
                        Error: {errorMessage}
                    </span>
                )}
            </div>
        </header>
    );
};