.RECIPEPREFIX := >
MODEL ?= llama3

.PHONY: check-ollama
check-ollama:
>command -v ollama >/dev/null 2>&1 || { echo 'Ollama is required: https://ollama.ai' >&2; exit 1; }
>ollama list | awk 'NR>1 {print $$1}' | grep -q "^$(MODEL)$$" || { echo 'Model $(MODEL) not found. Pull it with: ollama pull $(MODEL)' >&2; exit 1; }

.PHONY: dev
dev: check-ollama
>echo 'Starting backend and frontend (dev mode)...'
>trap 'kill 0' INT TERM EXIT; \
>uv run --directory server fastapi dev --host 0.0.0.0 --port 8000 & \
>pnpm --dir web dev -- --host 0.0.0.0 --port 5173 & \
>wait

.PHONY: start
start: check-ollama
>echo 'Starting backend and frontend (prod mode)...'
>trap 'kill 0' INT TERM EXIT; \
>uv run --directory server fastapi run --host 0.0.0.0 --port 8000 & \
>pnpm --dir web preview -- --host 0.0.0.0 --port 5173 & \
>wait

