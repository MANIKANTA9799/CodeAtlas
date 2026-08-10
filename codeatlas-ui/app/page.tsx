"use client";
import React, { useState } from "react";
import { IngestionHeader } from "../components/IngestionHeader";
import { ChatPanel } from "../components/ChatPanel";
// Import ContextPanel AND the SourceItem interface from it!
import { ContextPanel, SourceItem } from "../components/ContextPanel";

export default function Home() {
  const [activeProject, setActiveProject] = useState<string>("default_project");
  const [activeSources, setActiveSources] = useState<SourceItem[]>([]);

  return (
    <div className="flex flex-col h-screen bg-gray-950 overflow-hidden">

      {/* TOP NAVBAR: Handles Ingestion and dynamically sets the active project */}
      <IngestionHeader
        onProjectChange={(projectName) => setActiveProject(projectName)}
      />

      {/* MAIN WORKSPACE: Split between Chat and Context */}
      <div className="flex flex-1 overflow-hidden">

        {/* LEFT SIDE: Chat Interface */}
        <div className="flex-1 flex flex-col min-w-0 border-r border-gray-800">
          <ChatPanel
            projectName={activeProject}
            onSourcesUpdate={(sources) => setActiveSources(sources)}
          />
        </div>

        {/* RIGHT SIDE: Context Inspector */}
        <div className="w-1/3 flex flex-col min-w-0 bg-gray-900">
          <ContextPanel sources={activeSources} />
        </div>

      </div>
    </div>
  );
}