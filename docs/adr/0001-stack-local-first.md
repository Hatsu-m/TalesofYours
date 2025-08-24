# ADR 0001: Stack and Local-First Rationale

## Context

Tales of Yours aims to be a fully local-first tabletop RPG engine. The server is built with FastAPI and the web client uses React with TypeScript. Using a monorepo keeps engine, server, and web client code in a single place.

## Decision

- **FastAPI** for the server because of its async support and great developer experience.
- **React + Vite + TypeScript** for the web client for fast iteration and strong typing.
- **uv** manages Python dependencies; **pnpm** manages Node packages.
- **pre-commit**, **ruff**, **black**, **eslint**, and **typescript** ensure a consistent codebase.
- Data, models, and LLM interactions should operate without relying on cloud services; all models run locally.

## Status

Accepted.

## Consequences

- Developers can run the entire stack offline.
- A single `uv run fastapi dev` starts the backend, and `pnpm dev` starts the web app.
- Pre-commit hooks enforce formatting and static analysis for both Python and TypeScript code.
