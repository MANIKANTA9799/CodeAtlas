import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";
import { Check, Copy } from "lucide-react";

interface MarkdownBlockProps {
    content: string;
}

export const MarkdownBlock: React.FC<MarkdownBlockProps> = ({ content }) => {
    return (
        <div className="text-sm leading-relaxed">
            <ReactMarkdown
                rehypePlugins={[rehypeHighlight]}
                components={{
                    // Custom renderer for code blocks
                    code({ node, inline, className, children, ...props }: any) {
                        const match = /language-(\w+)/.exec(className || "");
                        const [copied, setCopied] = useState(false);

                        const handleCopy = () => {
                            navigator.clipboard.writeText(String(children).replace(/\n$/, ""));
                            setCopied(true);
                            setTimeout(() => setCopied(false), 2000);
                        };

                        // If it's a multi-line code block with a language specified
                        if (!inline && match) {
                            return (
                                <div className="relative group my-4 rounded-lg overflow-hidden border border-gray-700 bg-[#0d1117]">
                                    <div className="flex items-center justify-between px-4 py-2 bg-gray-900 border-b border-gray-700 text-xs text-gray-400">
                                        <span className="uppercase font-mono font-bold tracking-wider">{match[1]}</span>
                                        <button
                                            onClick={handleCopy}
                                            className="flex items-center space-x-1 hover:text-gray-200 transition-colors bg-gray-800 hover:bg-gray-700 px-2 py-1 rounded"
                                            title="Copy code"
                                        >
                                            {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
                                            <span>{copied ? "Copied!" : "Copy"}</span>
                                        </button>
                                    </div>
                                    <div className="p-4 overflow-x-auto text-[13px] font-mono">
                                        <code className={className} {...props}>
                                            {children}
                                        </code>
                                    </div>
                                </div>
                            );
                        }

                        // If it's inline code (e.g., `const x = 10;` inside a paragraph)
                        return (
                            <code className="bg-gray-800 text-blue-300 rounded px-1.5 py-0.5 text-[13px] font-mono" {...props}>
                                {children}
                            </code>
                        );
                    },
                    // Polish up standard Markdown elements
                    p: ({ children }) => <p className="mb-4 last:mb-0">{children}</p>,
                    ul: ({ children }) => <ul className="list-disc pl-5 mb-4 space-y-1">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal pl-5 mb-4 space-y-1">{children}</ol>,
                    h1: ({ children }) => <h1 className="text-xl font-bold mb-4 mt-6 text-gray-100">{children}</h1>,
                    h2: ({ children }) => <h2 className="text-lg font-bold mb-3 mt-5 text-gray-100">{children}</h2>,
                    h3: ({ children }) => <h3 className="text-md font-bold mb-2 mt-4 text-gray-100">{children}</h3>,
                    a: ({ children, href }) => <a href={href} className="text-blue-400 hover:underline" target="_blank" rel="noreferrer">{children}</a>,
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    );
};