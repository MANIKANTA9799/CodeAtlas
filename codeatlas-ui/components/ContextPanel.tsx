import React from "react";

export interface SourceItem {
    type: "code" | "commit";
    file_path?: string;
    symbol?: string;
    hash?: string;
    author?: string;
}

interface ContextPanelProps {
    sources: SourceItem[];
    retrievedContext?: string;
}

export const ContextPanel: React.FC<ContextPanelProps> = ({ sources, retrievedContext }) => {
    return (
        <div className="flex flex-col h-full bg-gray-900 border-l border-gray-800 p-4 overflow-y-auto">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3 mb-4">
                <h2 className="text-lg font-semibold text-gray-200">Context Inspector</h2>
                <span className="text-xs px-2 py-1 bg-gray-800 text-gray-400 rounded-md">
                    {sources.length} Sources Retained
                </span>
            </div>

            {sources.length === 0 ? (
                <div className="flex flex-col items-center justify-center flex-1 text-gray-500 text-sm">
                    <p>No active context retrieved.</p>
                    <p className="text-xs text-gray-600 mt-1">
                        Ask a question to inspect Qdrant search vectors.
                    </p>
                </div>
            ) : (
                <div className="space-y-4">
                    <div className="space-y-2">
                        <h3 className="text-xs font-uppercase tracking-wider text-gray-400 font-bold uppercase">
                            Retrieved Sources
                        </h3>
                        {sources.map((src, idx) => (
                            <div
                                key={idx}
                                className="p-3 bg-gray-950 border border-gray-800 rounded-lg text-sm space-y-1"
                            >
                                <div className="flex items-center justify-between">
                                    <span
                                        className={`text-xs font-mono font-semibold uppercase px-2 py-0.5 rounded ${src.type === "code"
                                                ? "bg-blue-950 text-blue-400 border border-blue-800"
                                                : "bg-purple-950 text-purple-400 border border-purple-800"
                                            }`}
                                    >
                                        {src.type}
                                    </span>
                                    {src.hash && (
                                        <span className="text-xs font-mono text-gray-500">
                                            #{src.hash.substring(0, 7)}
                                        </span>
                                    )}
                                </div>

                                {src.file_path && (
                                    <div className="font-mono text-xs text-gray-300 break-all pt-1">
                                        {src.file_path}
                                    </div>
                                )}

                                {src.symbol && (
                                    <div className="text-xs text-gray-400">
                                        Symbol: <span className="font-mono text-gray-200">{src.symbol}</span>
                                    </div>
                                )}

                                {src.author && (
                                    <div className="text-xs text-gray-400">
                                        Author: <span className="text-gray-300">{src.author}</span>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>

                    {retrievedContext && (
                        <div className="mt-6">
                            <h3 className="text-xs font-uppercase tracking-wider text-gray-400 font-bold uppercase mb-2">
                                Raw Retrieved Payload Block
                            </h3>
                            <pre className="p-3 bg-gray-950 border border-gray-800 rounded-lg text-xs font-mono text-gray-400 overflow-x-auto max-h-96 whitespace-pre-wrap">
                                {retrievedContext}
                            </pre>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};