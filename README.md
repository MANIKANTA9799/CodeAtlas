# CodeAtlas 🗺️

CodeAtlas is a fully localized, privacy-first AI codebase explorer. It allows you to ingest any local Git repository, chunk its syntax, and chat directly with your code using local Large Language Models (LLMs).

CodeAtlas features a dynamic multi-tenant architecture, allowing you to seamlessly swap between different projects and isolated Qdrant vector buckets on the fly. Because every component runs entirely on your local machine, **your code never leaves your laptop**.

---

## 🎯 Why CodeAtlas? (Use Cases)

CodeAtlas was built to solve the tension between developer velocity and code privacy. It is an indispensable tool for two critical phases of software development:

### 🚀 For Startup Founders & Indie Hackers

When you are bootstrapping a startup, your intellectual property is your most valuable asset. Sending your proprietary algorithms to third-party APIs introduces massive compliance and security risks.

* **Protect Your IP:** CodeAtlas gives you AI-assisted development with zero data exfiltration.
* **Context Switching:** Instantly swap your AI context between repositories.
* **Iterate Faster:** Recall how modules were built by querying local Git history.

### 🏢 For Enterprise Onboarding & Engineering Teams

Joining a new company or transitioning to a new team usually means weeks of reading documentation and understanding architectures.

* **Day-One Productivity:** Ask CodeAtlas about complex implementations instead of manually searching thousands of files.
* **Strict Compliance:** Local LLM and vector database execution keeps code on the machine.
* **Git History as Documentation:** Understand why decisions were made by querying historical commits.

---

## ✨ Features

* **100% Local Processing:** Powered by LangGraph and Ollama.
* **Smart Routing Engine:** Routes queries to source code, Git history, or both.
* **Isolated Project Workspaces:** Separate Qdrant vector buckets per repository.
* **Real-time Context Inspector:** View retrieved files, code blocks, and commits.
* **Streaming Responses:** Token-by-token markdown streaming with syntax highlighting.

---

## 🏗️ Architecture Stack

* **Frontend:** Next.js (React), Tailwind CSS, Server-Sent Events (SSE)
* **Backend:** FastAPI, Python, LangGraph
* **AI/LLM:** Ollama (Llama 3.1 default)
* **Vector Database:** Qdrant (Local persistent storage)
* **Ingestion:** GitPython, AST Chunking

---

## 🚀 Prerequisites

1. **Ollama:** Must be installed and running on your local machine.
2. Pull the default Llama 3.1 model:

```bash
ollama run llama3.1
```

3. **Docker:** Required for the containerized setup (Recommended).

---

## 🛠️ Getting Started

## Method A: Docker (Recommended)

1. Ensure Ollama is running in the background.
2. From the root directory:

```bash
docker-compose up --build
```

3. Open:

```
http://localhost:3000
```

---

## Method B: Manual Setup

### 1. Start the Backend

```bash
cd codeatlas-backend

pip install -r requirements.txt

uvicorn main:app --reload
```

### 2. Start the Frontend

```bash
cd codeatlas-ui

npm install

npm run dev
```

Navigate to:

```
http://localhost:3000
```

---

# 📖 How to Use

## Ingest a Repository

- Open the top navigation bar.
- Enter a custom **Bucket Name**.
- Paste the absolute path to your repository.
- Click **Ingest**.

Example:

```
C:\Users\Dev\core-backend
```

---

## Chat with your Code

Ask questions like:

> Explain the routing logic in api.py

or:

> What were the last 5 commits related to caching?

The Context Inspector will display the exact vectors retrieved by the AI.

---

## Swap Contexts on the Fly

- Click the **Bucket Name** input.
- Select an existing project.
- CodeAtlas switches AI search context instantly without re-ingestion.
