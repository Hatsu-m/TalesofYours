# Tales Of Yours

Tales Of Yours is a local-first, AI-powered tabletop RPG engine that gives you a personal AI Dungeon Master. Everything runs on your machine with no external services required.

## Features
- Local AI DM powered by [Ollama](https://ollama.ai/)
- Markdown-based worlds and rule files
- Automatic tracking of party members and world state
- Save and load game sessions
- Web interface for play

## Installation

### Windows

**Prerequisites**
- Python 3.11+
- Node.js 20+ with `pnpm`
- Git
- [Ollama](https://ollama.ai/) with a model such as `llama3`

**Steps**
1. Clone the repository and enter it:
   ```powershell
   git clone <repository-url>
   cd TalesofYours
   ```
2. Backend setup:
   ```powershell
   cd server
   uv venv
   uv pip install -r requirements.txt
   uv run fastapi dev
   ```
3. Frontend setup (in a new terminal):
   ```powershell
   cd ..\web
   pnpm install
   pnpm dev
   ```
   Backend runs on `http://localhost:8000` and the frontend on `http://localhost:5173`.

### Linux

**Prerequisites**
- Python 3.11+
- Node.js 20+ with `pnpm`
- Git
- [Ollama](https://ollama.ai/) with a model such as `llama3`

**Steps**
1. Clone the repository and enter it:
   ```bash
   git clone <repository-url>
   cd TalesofYours
   ```
2. Start backend and frontend together:
   ```bash
   make dev
   ```
   This launches the FastAPI backend and Vite frontend with hot reload.

**Manual setup**
```bash
# Backend
cd server
uv venv
uv pip install -r requirements.txt
uv run fastapi dev

# Frontend
cd ../web
pnpm install
pnpm dev
```

## License
Released under the MIT License.
