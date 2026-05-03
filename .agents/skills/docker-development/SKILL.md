---
name: docker-development
description: >-
  Codex runtime skill generated from canonical `skills/docker-development/SKILL.md`. Dockerfile optimization, multi-stage builds, docker-compose best practices, and container security hardening.
---

# docker-development (Codex Runtime Skill)

Canonical source: `skills/docker-development/SKILL.md`

This file is self-contained for Codex runtime. Shared behavior belongs
in the canonical source skill; regenerate this file after changing the
source.

## Codex Runtime Notes

- Prefer `AGENTS.md` for root guidance. Treat `CLAUDE.md` only as supplemental fallback when older Claude-specific text in the inlined body requires it.
- Use Codex-native tools and `.agents/skills/`; translate older Claude coordination wording in the body into explicit user requests, current tools, or durable artifacts when the workflow requires them.

## Classification

- Migration category: Generate as Codex runtime skill
- Rationale: Workflow or reference guidance is useful in Codex as a self-contained runtime skill.

## Inlined Skill Body

## Docker Development

Opinionated patterns for building production-grade containers.

---

### Purpose

- Produce smaller, faster, more secure container images
- Prevent common Dockerfile and compose anti-patterns
- Enforce security hardening as a default, not an afterthought

---

### Dockerfile Optimization

#### Base Image

- Pin specific version tags (never `:latest` in production)
- Prefer slim variants: `python:3.12-slim` over `python:3.12`
- Pin digests for CI reproducibility: `image@sha256:...`

#### Layer Ordering

1. Copy dependency files first (`requirements.txt`, `package.json`)
2. Install dependencies (maximizes cache hits)
3. Copy source code last (changes most frequently)
4. Never `COPY . .` before dependency installation

#### Layer Hygiene

- Combine related RUN commands with `&&`
- Clean package cache in the same RUN layer:
  `apt-get install -y pkg && rm -rf /var/lib/apt/lists/*`
- Use `.dockerignore`: `.git`, `__pycache__`, `.env`, `*.log`, `.vscode`,
  `coverage`, `.pytest_cache`, `node_modules`

---

### Multi-Stage Build: Python

```dockerfile
FROM python:3.12-slim AS builder
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /install /usr/local
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
COPY . /app
WORKDIR /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Key principles:
- Builder stage has build tools; runtime stage has only production artifacts
- `--prefix=/install` isolates pip output for clean copy
- Non-root user created in runtime stage
- No dev dependencies in final image

---

### Docker Compose Best Practices

#### Service Configuration

- Use `depends_on` with `condition: service_healthy` for startup ordering
- Add HEALTHCHECK to every service (interval, timeout, retries)
- Set resource limits (`mem_limit`, `cpus`)
- Pin image versions

#### Networking

- Create explicit named networks (do not rely on default bridge)
- Separate frontend and backend networks
- Use `internal: true` for backend-only networks (prevents external DB access)
- Only expose ports that need external access

#### Environment Variables

- Use `env_file` for secrets, never inline in compose
- Never commit `.env` files (add to `.gitignore`)
- Use defaults: `${VAR:-default_value}`
- Document all required vars in a committed `.env.example`

#### Dev vs Production

- Dev: bind mounts for hot reload, debug ports exposed
- Prod: named volumes, no debug ports, `restart: unless-stopped`
- Use `docker-compose.override.yml` for dev (auto-loaded locally)

---

### Security Checklist

| Issue | Severity | Fix |
|-------|----------|-----|
| Running as root | CRITICAL | Add `USER nonroot` after user creation |
| `:latest` tag | HIGH | Pin to specific version |
| Secrets in ENV/ARG | CRITICAL | Use BuildKit secrets: `--mount=type=secret` |
| Broad COPY glob | MEDIUM | Use specific paths + `.dockerignore` |
| No HEALTHCHECK | MEDIUM | Add with appropriate interval |
| Writable root filesystem | MEDIUM | Use `read_only: true` + tmpfs for /tmp |
| All capabilities retained | HIGH | `cap_drop: [ALL]`, add only what is needed |
| Docker socket mounted | CRITICAL | Never mount in production |
| No log size limits | LOW | Set `max-size: 10m`, `max-file: 3` |

---

### Proactive Triggers

Flag these issues without being asked:

- Dockerfile uses `:latest` -- suggest pinning
- No `.dockerignore` -- create one with standard exclusions
- `COPY . .` before dependency install -- cache bust risk
- Running as root -- add USER instruction
- Secrets in ENV or ARG -- recommend BuildKit secret mounts
- Image over 1GB -- multi-stage build required
- No healthcheck -- add for orchestration lifecycle
- `apt-get` without cleanup in same layer -- flag missing cache removal

---

### Guidelines

**Do:**
- Default to multi-stage builds for all production images
- Run as non-root user in every container
- Separate build-time and runtime dependencies
- Test with `docker compose config` before deploying

**Don't:**
- Use `:latest` in production
- Commit `.env` files
- Expose debug ports in production compose
- Mount the Docker socket in application containers

---

### Debugging Containers

#### Crash-Looping Containers

When a container fails to start (missing env vars, missing files), `restart: unless-stopped` keeps restarting it. Every `docker exec` attempt fails with "container is restarting."

**Fix:** Run `docker compose down` or `docker stop` first, then `docker logs <container>` to see the error. Do not attempt `docker exec` on a restarting container.
