# Guidance

In-repo guidance for `news_site`. The `compound` skill writes feedback
captures here; standing instructions for working in this repo also live here.
This file is auto-loaded into every Claude/Codex session via the `@`-imports
in `CLAUDE.md` and `AGENTS.md`.

## Standing Rules

### Conventions: ASCII-only markdown, logging/exception patterns

- All markdown files use ASCII only (no emojis, no Unicode symbols)
- Logging via Python logging module (no print statements)
- Error handling via custom exception hierarchy (core/exceptions.py)

### Environment Variables

- ANTHROPIC_API_KEY: Claude API key (required for story writer)
- DATABASE_URL: Database connection string (defaults to SQLite)

### Key testing patterns: coverage targets, test-driven behavior

```bash
make test
# or: cd backend && pytest tests/ -v
```

- Coverage targets: 80%+ for new modules, 90%+ for critical paths
- Test paths: `backend/tests/`

### Dev/Prod Parity

Keep development and production environments as similar as possible. If production runs in containers, develop and test in containers. Use compose overlays (`docker-compose.yml` + `docker-compose.override.yml`) to manage necessary differences (exposed ports, volume mounts, debug flags) rather than maintaining separate toolchains. Differences between environments are where bugs hide.
