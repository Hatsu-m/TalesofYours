# AGENTS

## General Guidelines
- Run `pre-commit run --files <files>` before committing. For documentation-only changes, you may skip frontend hooks using `SKIP=frontend-lint,frontend-typecheck`.
- For Python code changes, ensure `pytest` passes.
- For frontend changes under `web/`, run `pnpm lint` and `pnpm typecheck`.
- Keep commit messages clear and leave the worktree clean.
