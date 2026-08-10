import React, { useState, useEffect } from "react";

interface IngestionHeaderProps {
    onIngestSuccess?: () => void;
    onProjectChange?: (projectName: string) => void;
}

export const IngestionHeader: React.FC<IngestionHeaderProps> = ({ onIngestSuccess, onProjectChange }) => {
    const [repoPath, setRepoPath] = useState("");
    const [customProjectName, setCustomProjectName] = useState("");

    // NEW STATE: For the dropdown suggestions
    const [availableProjects, setAvailableProjects] = useState<string[]>([]);
    const [showDropdown, setShowDropdown] = useState(false);

    const [status, setStatus] = useState<"idle" | "code" | "git" | "complete" | "error">("idle");
    const [errorMessage, setErrorMessage] = useState("");
    const [elapsedTime, setElapsedTime] = useState<number | null>(null);

    // NEW: Fetch existing collections when the header loads
    useEffect(() => {
        fetch("http://127.0.0.1:8000/api/v1/ingest/collections")
            .then(res => res.json())
            .then(data => {
                if (data.collections) setAvailableProjects(data.collections);
            })
            .catch(err => console.error("Failed to fetch collections", err));
    }, []);

    const handleIngest = async () => {
        if (!repoPath.trim()) return;

        setStatus("code");
        setErrorMessage("");
        setElapsedTime(null);
        const startTime = Date.now();

        let finalProjectName = customProjectName.trim();
        if (!finalProjectName) {
            const normalizedPath = repoPath.replace(/\\/g, "/").replace(/\/$/, "");
            finalProjectName = normalizedPath.split("/").pop() || "default_project";
            setCustomProjectName(finalProjectName);
        }

        if (onProjectChange) onProjectChange(finalProjectName);

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

            // Add the newly ingested project to the dropdown list so it appears immediately!
            if (!availableProjects.includes(finalProjectName)) {
                setAvailableProjects(prev => [...prev, finalProjectName]);
            }

            if (onIngestSuccess) onIngestSuccess();
        } catch (err: any) {
            setStatus("error");
            setErrorMessage(err.message || "An unknown error occurred");
        }
    };

    return (
        <div className="flex items-center justify-between p-4 bg-gray-950 border-b border-gray-800 shadow-sm relative z-50">
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

                {/* --- THE NEW SEARCH BAR WITH DROPDOWN --- */}
                <div className="relative">
                    <input
                        type="text"
                        value={customProjectName}
                        onChange={(e) => {
                            setCustomProjectName(e.target.value);
                            setShowDropdown(true);
                            if (onProjectChange) onProjectChange(e.target.value);
                        }}
                        onFocus={() => setShowDropdown(true)}
                        // Delay closing so the user's click registers before the menu disappears
                        onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
                        placeholder="Bucket Name"
                        className="w-40 bg-gray-900 border border-gray-800 rounded-md px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-blue-500 font-mono transition-colors"
                    />

                    {/* Autocomplete Suggestions Menu */}
                    {showDropdown && availableProjects.length > 0 && (
                        <div className="absolute top-full left-0 mt-1 w-full bg-gray-900 border border-gray-700 rounded-md shadow-xl overflow-hidden z-50">
                            {availableProjects
                                .filter(p => p.toLowerCase().includes(customProjectName.toLowerCase()))
                                .slice(0, 5) // Keep it clean: Top 5 only
                                .map(project => (
                                    <div
                                        key={project}
                                        onClick={() => {
                                            setCustomProjectName(project);
                                            if (onProjectChange) onProjectChange(project);
                                            setShowDropdown(false);
                                        }}
                                        className="px-3 py-2 text-sm text-gray-300 hover:bg-blue-600 hover:text-white cursor-pointer font-mono truncate transition-colors"
                                    >
                                        {project}
                                    </div>
                                ))}
                        </div>
                    )}
                </div>
                {/* ---------------------------------------- */}

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