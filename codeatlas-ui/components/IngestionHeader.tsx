import React, { useState } from "react";

interface IngestionHeaderProps {
    onIngestSuccess?: () => void;
    onProjectChange?: (projectName: string) => void;
}

export const IngestionHeader: React.FC<IngestionHeaderProps> = ({ onIngestSuccess, onProjectChange }) => {
    const [repoPath, setRepoPath] = useState("");
    const [customProjectName, setCustomProjectName] = useState("");
    const [status, setStatus] = useState<"idle" | "code" | "git" | "complete" | "error">("idle");
    const [errorMessage, setErrorMessage] = useState("");
    const [elapsedTime, setElapsedTime] = useState<number | null>(null);

    const handleIngest = async () => {
        if (!repoPath.trim()) return;

        setStatus("code");
        setErrorMessage("");
        setElapsedTime(null);
        const startTime = Date.now();

        // 1. Determine Project Name (Use explicit input, otherwise fallback to folder name)
        let finalProjectName = customProjectName.trim();
        if (!finalProjectName) {
            const normalizedPath = repoPath.replace(/\\/g, "/").replace(/\/$/, "");
            finalProjectName = normalizedPath.split("/").pop() || "default_project";
            setCustomProjectName(finalProjectName); // Fill the UI with the extracted name
        }

        // Lift state to main page
        if (onProjectChange) {
            onProjectChange(finalProjectName);
        }

        try {
            const codeRes = await fetch("http://127.0.0.1:8000/api/v1/ingest/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    repo_path: repoPath.trim(),
                    project_name: finalProjectName,
                }),
            });

            if (!codeRes.ok) throw new Error("Code ingestion failed");

            setStatus("git");
            const gitRes = await fetch("http://127.0.0.1:8000/api/v1/ingest/git", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    repo_path: repoPath.trim(),
                    project_name: finalProjectName,
                }),
            });

            if (!gitRes.ok) throw new Error("Git ingestion failed");

            setStatus("complete");
            setElapsedTime(Math.round((Date.now() - startTime) / 1000));
            if (onIngestSuccess) onIngestSuccess();
        } catch (err: any) {
            setStatus("error");
            setErrorMessage(err.message || "An unknown error occurred");
        }
    };

    return (
        <div className="flex items-center justify-between p-4 bg-gray-950 border-b border-gray-800 shadow-sm">
            {/* LEFT: Branding & Agent Status */}
            <div className="flex items-center space-x-4">
                <h1 className="text-xl font-bold text-gray-100 tracking-wide">CodeAtlas</h1>
                <span className="text-xs text-green-400 bg-green-950 border border-green-800 px-2.5 py-1 rounded-full flex items-center space-x-1.5">
                    <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                    <span>Agent Online</span>
                </span>
            </div>

            {/* RIGHT: Explicit Inputs & Controls */}
            <div className="flex items-center space-x-3">
                {status === "complete" && (
                    <span className="text-green-400 font-mono text-xs px-2">✓ {elapsedTime}s</span>
                )}
                {status === "error" && (
                    <span className="text-red-400 font-mono text-xs px-2 truncate max-w-[200px]" title={errorMessage}>
                        Error: {errorMessage}
                    </span>
                )}

                {/* The New Project Name Input */}
                <input
                    type="text"
                    value={customProjectName}
                    onChange={(e) => {
                        setCustomProjectName(e.target.value);
                        if (onProjectChange) onProjectChange(e.target.value); // Keep ChatPanel in sync while typing!
                    }}
                    placeholder="Bucket Name"
                    className="w-36 bg-gray-900 border border-gray-800 rounded-md px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500 font-mono transition-colors"
                />

                <input
                    type="text"
                    value={repoPath}
                    onChange={(e) => setRepoPath(e.target.value)}
                    placeholder="C:\Path\To\Repository"
                    className="w-64 bg-gray-900 border border-gray-800 rounded-md px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500 font-mono transition-colors"
                />

                <button
                    onClick={handleIngest}
                    disabled={status === "code" || status === "git"}
                    className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 text-white text-sm font-semibold px-5 py-2 rounded-md transition-all whitespace-nowrap"
                >
                    {status === "code" ? "Indexing..." : status === "git" ? "Scanning Git..." : "Ingest"}
                </button>
            </div>
        </div>
    );
};