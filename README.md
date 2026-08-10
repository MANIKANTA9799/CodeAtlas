CodeAtlas 🗺️
CodeAtlas is a fully localized, privacy-first AI codebase explorer. It allows you to ingest any local Git repository, chunk its syntax, and chat directly with your code using local Large Language Models (LLMs).

CodeAtlas features a dynamic multi-tenant architecture, allowing you to seamlessly swap between different projects and isolated Qdrant vector buckets on the fly. Because every component runs entirely on your local machine, your code never leaves your laptop.

🎯 Why CodeAtlas? (Use Cases)
CodeAtlas was built to solve the tension between developer velocity and code privacy. It is an indispensable tool for two critical phases of software development:

🚀 For Startup Founders & Indie Hackers
When you are bootstrapping a startup, your intellectual property is your most valuable asset. Sending your proprietary algorithms—whether that's a novel computer vision model, a cybersecurity attack path predictor, or high-performance C++ systems—to third-party APIs like OpenAI or Anthropic introduces massive compliance and security risks.

Protect Your IP: CodeAtlas gives you the power of AI-assisted development with zero data exfiltration.

Context Switching: Founders wear many hats. Use the UI dropdown to instantly swap your AI's context from your frontend React repository to your backend Python services without missing a beat.

Iterate Faster: Instantly recall how a specific module was built three months ago by querying your local Git commit history.

🏢 For Enterprise Onboarding & Engineering Teams
Joining a new company or transitioning to a new team usually means weeks of reading stale documentation and deciphering complex architectures.

Day-One Productivity: Point CodeAtlas at the company's repository on your first day. Instead of pinging senior engineers to explain how the Java microservices implement Abstract Factory or Builder patterns, just ask CodeAtlas.

Strict Compliance: Because the LLM and vector database run locally, companies can safely mandate CodeAtlas for new hires without violating NDAs, SOC2 compliance, or enterprise data policies. The code stays on the corporate-issued laptop.

Git History as Documentation: Understand why a decision was made by asking the smart routing engine to search historical Git commits and author metadata.

✨ Features
100% Local Processing: Powered by LangGraph and Ollama. No data, prompts, or code snippets are ever transmitted over the internet.

Smart Routing Engine: Intelligently categorizes your query and routes it to search active source code, historical Git commits, or both.

Isolated Project Workspaces: Ingest multiple repositories into physically separate Qdrant vector buckets. Ensure zero cross-contamination of context.

Real-time Context Inspector: Verify the AI's reasoning. See the exact files, code blocks, and commits the agent is reading in the right-hand inspection panel.

Streaming Responses: Enjoy lightning-fast, token-by-token streaming with real-time markdown rendering and syntax highlighting.

🏗️ Architecture Stack
Frontend: Next.js (React), Tailwind CSS, Server-Sent Events (SSE)

Backend: FastAPI, Python, LangGraph

AI/LLM: Ollama (Llama 3.1 default)

Vector Database: Qdrant (Local persistent storage)

Ingestion: GitPython, AST Chunking

🚀 Prerequisites
Ollama: Must be installed and running on your local machine.

Local Model: Pull the default Llama 3.1 model by running the following command in your terminal:

Bash
ollama run llama3.1
Docker: Required if you plan to use the containerized setup (Recommended).

🛠️ Getting Started
Method A: Docker (Recommended)
The fastest way to get started is by spinning up the entire stack using Docker Compose.

Ensure Ollama is running in the background on your host machine.

From the root directory of the project, run:

Bash
docker-compose up --build
Open http://localhost:3000 in your browser.

Method B: Manual Setup
If you prefer to run the services bare-metal, follow these steps:

1. Start the Backend

Bash
cd codeatlas-backend
# Optional: Create a virtual environment first
pip install -r requirements.txt
uvicorn main:app --reload
2. Start the Frontend

Bash
cd codeatlas-ui
npm install
npm run dev
Once both servers are running, navigate to http://localhost:3000.

📖 How to Use
Ingest a Repository:

Look at the top navigation bar.

Type a custom Bucket Name (e.g., core-backend) to create an isolated workspace.

Paste the absolute path to a local repository on your hard drive (e.g., C:\Users\Dev\core-backend).

Click Ingest and wait for the success confirmation.

Chat with your Code:

Ask a natural language question in the chat panel (e.g., "Explain the routing logic in api.py" or "What were the last 5 commits related to caching?").

Watch the Context Inspector on the right populate with the exact vectors the AI retrieved.

Swap Contexts on the Fly:

Click the Bucket Name input in the top navigation bar.

A dropdown will appear listing all your previously ingested projects.

Select a different project to instantly redirect the AI's search focus—no re-ingestion required.
