"use client";

import React, { useState } from "react";
import { ChatPanel } from "@/components/ChatPanel";
import { ContextPanel, SourceItem } from "@/components/ContextPanel";

export default function Home() {
  const [activeSources, setActiveSources] = useState<SourceItem[]>([]);

  return (
    <main className="flex h-screen w-screen overflow-hidden bg-gray-950">
      {/* Left Lane: 60% Width */}
      <div className="w-3/5 h-full">
        <ChatPanel onSourcesUpdate={(sources) => setActiveSources(sources)} />
      </div>

      {/* Right Lane: 40% Width */}
      <div className="w-2/5 h-full">
        <ContextPanel sources={activeSources} />
      </div>
    </main>
  );
}