"use client";

import React, { useState } from "react";
import { IngestionHeader } from "@/components/IngestionHeader";
import { ChatPanel } from "@/components/ChatPanel";
import { ContextPanel, SourceItem } from "@/components/ContextPanel";

export default function Home() {
  const [activeSources, setActiveSources] = useState<SourceItem[]>([]);
  // We track the current repo path in case we want to display it in the UI later
  const [currentRepo, setCurrentRepo] = useState<string | null>(null);

  return (
    <main className="flex flex-col h-screen w-screen overflow-hidden bg-gray-950">
      {/* Top Bar: Repository Ingestion Controls */}
      <IngestionHeader onIngestionComplete={(path) => setCurrentRepo(path)} />

      {/* Main Workspace: 2-Lane Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Lane: Chat Interface (60%) */}
        <div className="w-3/5 h-full relative">
          <ChatPanel onSourcesUpdate={(sources) => setActiveSources(sources)} />
        </div>

        {/* Right Lane: Context Inspector (40%) */}
        <div className="w-2/5 h-full relative">
          <ContextPanel sources={activeSources} />
        </div>
      </div>
    </main>
  );
}