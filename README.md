# Local AI TTRPG Engine (ACE-1 Inspired)

This project is a local-first, AI-powered tabletop RPG engine inspired by **ACE-1** (Agentic Campaign Engine).  
It lets you play solo TTRPG campaigns with a local AI Dungeon Master powered by **Ollama**.  
Players physically roll dice, type the results, and the AI DM continues narration while the engine maintains world state, companions, and rules.

---

## ✨ Features
- **Local AI DM** via [Ollama](https://ollama.ai/)
- **Markdown-based world editor** – easy to create and share custom worlds, stories, and rules
- **Player-rolled dice** – AI DM asks, player rolls, types result, engine resolves
- **Automatic memory & state tracking** – engine updates NPCs, items, quests, locations automatically
- **Party system** – recruit up to 3 companions and 2 pets (AI-controlled)
- **Save/Load & Export** – exportable game states and portable world files
- **Web UI** – professional browser-based interface built with React + Tailwind

---

## 🏗️ Tech Stack
- **Backend:** Python 3.11, FastAPI, SQLAlchemy (SQLite by default)
- **Engine:** Python package with rules plug-ins (D&D 5e, custom systems)
- **LLM Orchestration:** Ollama (local LLM runtime)
- **Frontend:** React + TypeScript + Vite + TailwindCSS
- **World Authoring:** Markdown with YAML frontmatter
- **Testing:** Pytest (backend), Vitest & Playwright (frontend)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+ (with pnpm or npm)
- [Ollama installed](https://ollama.ai/) and at least one model pulled (e.g. `llama2:13b`)

### Setup
```bash
# Clone repo
git clone https://github.com/your-username/local-ai-ttrpg.git
cd local-ai-ttrpg

# Backend setup
cd server
uv venv
uv pip install -r requirements.txt
uv run fastapi dev

# Frontend setup
cd ../web
pnpm install
pnpm dev
```

Backend runs on `http://localhost:8000`  
Frontend runs on `http://localhost:5173`

---

## 🎲 Gameplay Loop
1. Player types an **action** (`"I open the chest"`).  
2. AI DM narrates and may **request a roll** (`"Roll a d20 for Perception (DC 15)"`).  
3. Player physically rolls dice and **types the result**.  
4. Engine applies rules, updates memory & database automatically.  
5. AI DM continues narration.  

---

## 📂 Project Structure
```
/engine     # Core game engine & rules plug-ins
/server     # FastAPI backend + LLM orchestration
/web        # React frontend
/worlds     # Example Markdown worlds
/saves      # Game states & logs
/docs       # ADRs, API docs
```

---

## 🛠 Development Phases
The project is divided into small phases (0 → 21), each focusing on a single feature:  
- **Phase 0–2:** Scaffolding, Ollama adapter, core DB models  
- **Phase 3–5:** Markdown world loader, memory system, rules plug-in interface  
- **Phase 6–8:** Turn loop orchestration, roll request/response system, player-roll endpoint  
- **Phase 9–12:** Companions/pets, save/load, REST API, frontend scaffold  
- **Phase 13–15:** Streaming chat, player roll UI, in-app world editor  
- **Phase 16–18:** Rule switching, companion personalities, autosave/recovery  
- **Phase 19–21:** UI polish, theming, packaging one-click local run  

See [`/docs/`](./docs) for detailed architecture notes.

---

## 📜 License
MIT – free to use and modify.
