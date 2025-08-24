diff --git a/README.md b/README.md
index 9269d2821c577e65f1657a8d304b7a62d22910cd..ce7688b0443d4b8c09c62dfa540485714aa8aff7 100644
--- a/README.md
+++ b/README.md
@@ -1,108 +1,49 @@
-# Local AI TTRPG Engine (ACE-1 Inspired)
+# Tales Of Yours
 
-This project is a local-first, AI-powered tabletop RPG engine inspired by **ACE-1** (Agentic Campaign Engine).  
-It lets you play solo TTRPG campaigns with a local AI Dungeon Master powered by **Ollama**.  
-Players physically roll dice, type the results, and the AI DM continues narration while the engine maintains world state, companions, and rules.
+Tales Of Yours is a local-first, AI-powered tabletop RPG engine that runs entirely on your machine. It provides a personal AI Dungeon Master and tools for creating and playing immersive adventures.
 
----
+## Features
+- Local AI Dungeon Master powered by [Ollama](https://ollama.ai/)
+- Markdown-based worlds and rule files
+- Automatic tracking of party members and world state
+- Save and load game sessions
+- Web interface for gameplay
 
-## ✨ Features
-- **Local AI DM** via [Ollama](https://ollama.ai/)
-- **Markdown-based world editor** – easy to create and share custom worlds, stories, and rules
-- **Player-rolled dice** – AI DM asks, player rolls, types result, engine resolves
-- **Automatic memory & state tracking** – engine updates NPCs, items, quests, locations automatically
-- **Party system** – recruit up to 3 companions and 2 pets (AI-controlled)
-- **Save/Load & Export** – exportable game states and portable world files
-- **Web UI** – professional browser-based interface built with React + Tailwind
+## Installation
 
----
-
-## 🏗️ Tech Stack
-- **Backend:** Python 3.11, FastAPI, SQLAlchemy (SQLite by default)
-- **Engine:** Python package with rules plug-ins (D&D 5e, custom systems)
-- **LLM Orchestration:** Ollama (local LLM runtime)
-- **Frontend:** React + TypeScript + Vite + TailwindCSS
-- **World Authoring:** Markdown with YAML frontmatter
-- **Testing:** Pytest (backend), Vitest & Playwright (frontend)
-
----
-
-## 🚀 Getting Started
-
-### Prerequisites
+### Requirements
 - Python 3.11+
 - Node.js 20+ (with pnpm or npm)
-- [Ollama installed](https://ollama.ai/) and at least one model pulled (e.g. `llama2:13b`)
-
-### Setup
-### One-command dev
-
-With [Ollama](https://ollama.ai) and the `llama3` model installed:
-
-```bash
-make dev
-```
-
-This launches both the FastAPI backend and the Vite frontend.
-
-### Manual setup
-
-```bash
-# Clone repo
-git clone https://github.com/your-username/local-ai-ttrpg.git
-cd local-ai-ttrpg
-
-# Backend setup
-cd server
-uv venv
-uv pip install -r requirements.txt
-uv run fastapi dev
-
-# Frontend setup
-cd ../web
-pnpm install
-pnpm dev
-```
-
-Backend runs on `http://localhost:8000`
-Frontend runs on `http://localhost:5173`
-
----
-
-## 🎲 Gameplay Loop
-1. Player types an **action** (`"I open the chest"`).  
-2. AI DM narrates and may **request a roll** (`"Roll a d20 for Perception (DC 15)"`).  
-3. Player physically rolls dice and **types the result**.  
-4. Engine applies rules, updates memory & database automatically.  
-5. AI DM continues narration.  
-
----
-
-## 📂 Project Structure
-```
-/engine     # Core game engine & rules plug-ins
-/server     # FastAPI backend + LLM orchestration
-/web        # React frontend
-/worlds     # Example Markdown worlds
-/saves      # Game states & logs
-/docs       # ADRs, API docs
-```

-
-See [`/docs/`](./docs) for detailed architecture notes.
-
----
-
-## 📜 License
-MIT – free to use and modify.
+- [Ollama](https://ollama.ai/) with at least one model installed (e.g. `llama3`)
+
+### Steps
+1. Clone the repository and enter it:
+   ```bash
+   git clone <repository-url>
+   cd TalesofYours
+   ```
+2. Start the development environment (backend and frontend):
+   ```bash
+   make dev
+   ```
+   Backend runs on `http://localhost:8000`
+   Frontend runs on `http://localhost:5173`
+
+**Manual setup**
+
+3. Backend:
+   ```bash
+   cd server
+   uv venv
+   uv pip install -r requirements.txt
+   uv run fastapi dev
+   ```
+4. Frontend:
+   ```bash
+   cd ../web
+   pnpm install
+   pnpm dev
+   ```
+
+## License
+This project is released under the MIT License. You are free to use, modify, and distribute it for any purpose.
