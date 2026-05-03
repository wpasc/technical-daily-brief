---
name: devops-practices
description: >-
  CI/CD pipeline patterns, infrastructure-as-code guidance, and deployment
  strategies with rollback procedures.
  TRIGGER when: setting up CI/CD pipelines, writing Terraform or IaC,
  planning deployment strategies, or designing rollback procedures.
  DO NOT TRIGGER when: working on application code, container configuration
  (use docker-development), or database migrations (use migration-strategy).
user-invocable: false
---

# DevOps Practices

CI/CD, infrastructure-as-code, and deployment patterns.

---

## Purpose

- Guide CI/CD pipeline design for reliable, repeatable builds
- Inform IaC tool selection and module structure
- Provide deployment strategies with tested rollback paths

---

## CI/CD Pipeline Patterns

### Stage Structure

1. **Build and Test**: checkout, install deps, lint, test with coverage
2. **Build Artifact**: Docker image build and push (tagged with commit SHA)
3. **Deploy**: conditional on branch (main only), uses artifact from step 2

### Key Principles

- Trigger on push to main/develop and on pull requests
- Conditional deployment: only deploy from main branch
- Chain stages with explicit dependencies (no implicit ordering)
- Upload coverage and test artifacts for visibility
- Pin all action/plugin versions (no `@latest`)

### Caching Strategy

- Cache dependency directories (node_modules, .venv, ~/.cache/pip)
- Key on lockfile hash (package-lock.json, requirements.txt)
- Restore keys with prefix fallback for partial cache hits

---

## Infrastructure as Code

### Tool Selection

| Tool | Use When |
|------|----------|
| Terraform/OpenTofu | Default for multi-cloud. HCL is declarative and well-supported. |
| Pulumi | Team prefers TypeScript/Python/Go for infra definitions |
| CloudFormation/Bicep | 100% single-cloud commitment with specific feature needs |

**Default to Terraform** unless there is a concrete reason to choose otherwise.

### Module Structure

- Validate before plan, plan before apply
- Remote state in object storage (S3, GCS, Azure Blob)
- State locking to prevent concurrent modifications
- Separate modules per concern (networking, compute, database)
- Pin provider versions

### Environment Promotion

- Infrastructure changes follow the same PR review process as code
- Promote through environments: dev -> staging -> production
- Use workspace or directory separation per environment
- Never apply to production without staging validation

---

## Deployment Strategies

### Blue-Green

- Maintain two identical environments (blue and green)
- Deploy new version to inactive environment
- Health-check gate: readiness probe must pass before traffic switch
- Switch traffic (load balancer, DNS, or Kubernetes service)
- Keep previous environment warm for quick rollback

### Rolling

- Gradually replace instances with new version
- Set max unavailable and max surge parameters
- Health checks gate each batch before proceeding
- Slower rollout but requires fewer resources than blue-green

### Canary

- Deploy to a small percentage of traffic first
- Monitor error rates and latency against baseline
- Gradually increase traffic percentage if metrics hold
- Automated rollback if metrics degrade

---

## Rollback Procedures

| Strategy | Method | Speed |
|----------|--------|-------|
| Blue-Green | Switch traffic back to previous environment | Seconds |
| Rolling | `kubectl rollout undo` or redeploy previous version | Minutes |
| Canary | Route all traffic to stable version | Seconds |
| Infrastructure | Apply previous Terraform state or revert IaC commit | Minutes |

### Rollback Checklist

1. Detect: automated monitoring or manual observation
2. Decide: compare error rate against rollback threshold
3. Execute: use the strategy-appropriate rollback method
4. Verify: health check the rolled-back version
5. Communicate: notify stakeholders of rollback and cause
6. Investigate: root-cause the failure before re-attempting

---

## Multi-Cloud Decision

**Default: single cloud.** Lower operational complexity, better managed
service integration, cost leverage from commitment.

Add a second cloud only with a concrete driver:
- Compliance or data residency requirements
- Company acquisition brought a different cloud
- Best-of-breed service not available on primary cloud

---

## Guidelines

**Do:**
- Pin all versions (actions, providers, base images)
- Gate deployments on health checks, not timers
- Test rollback procedures in staging regularly
- Keep IaC changes in the same PR review flow as application code

**Don't:**
- Deploy to production without staging validation
- Use `@latest` for any CI/CD action or plugin
- Skip health check gates under time pressure
- Go multi-cloud without a concrete business driver

---

## Deployment Verification

### Deploy One Layer at a Time

When deploying or wiring infrastructure, verify each layer before adding the next:

1. Container starts and healthcheck passes via `docker exec curl`
2. Env vars are correct inside the container via `docker exec env | grep PREFIX`
3. App-specific commands work via `docker exec <container> <command>`
4. Only then wire NGINX/proxy and verify externally

Never debug two layers at once. Each piece may be simple; the interactions create hours of debugging when multiple layers are changed before any single one is verified.

### NGINX Location Matching

Always use exact match (`location = /health`) for static NGINX health endpoints. Default prefix matching means `location /health` will match `/healthz`, `/healthz/ingestion`, and anything else starting with `/health`.

When debugging "wrong response from every endpoint," check NGINX location matching before investigating the application.

### Keep Infra Configs in Sync

When removing or renaming application components (dropping a frontend, changing container names), update all infra configs in the same commit. Treat NGINX configs, docker-compose files, and systemd units as part of the application, not separate infrastructure. If configs live in a different repo, update both repos together.

---

## Runtime Forensics

When investigating a running Linux service, use the right tool for the
question. Do not guess at system state when you can measure it.

| Question | Tool | Note |
|---|---|---|
| Is the process alive? exit code? | `systemctl status <service>`, `journalctl -u <service>` | Check for `code=exited, status=137` (oom-kill) |
| What is the memory breakdown? | `cat /sys/fs/cgroup/.../memory.stat \| head -3` | anon = heap (real usage), file = kernel page cache (reclaimable), kernel = small. DO NOT use `docker stats memory.current` for "leak" claims -- it sums all three. |
| What allocated this RSS? | `/proc/<pid>/status` (`VmRSS`, `VmPeak`), `pmap -x <pid>` | Tracks the actual process memory map |
| Was this container OOM-killed? | `dmesg \| grep -i "killed process"` | Records the cgroup, total-vm at kill time |
| What sockets is it holding? | `ss -tnlp` | Replaces `netstat` |
| What is it spending CPU on? | `py-spy top --pid <pid>` (Python), `perf top -p <pid>` (native) | Sampling profilers for live processes |
| Why did this systemd timer fail? | `systemctl list-timers --all`, `journalctl -u <service> --since "1 hour ago"` | Check both the timer and the service unit |

**The cgroup `memory.stat` rule**: before claiming any container has a
memory leak, read the cgroup memory breakdown directly. If `anon` (heap)
is flat and only `file` (page cache) grows, there is no leak -- the kernel
is doing its job caching recently-touched files. See the `Measurement
Before Attribution` principle in `standards/software-project-principles.md`.

---

## Live-Where Framework

**One-sentence framework:** Project owns what it emits and what its failure
modes look like. Shared infra (e.g., `project_infra`) owns the tools that
consume those emissions. When something must live in the consuming tool's
format (Grafana JSON, Prometheus rule YAML), the source-of-truth still
lives in the project and is pushed into the tool at deploy time.

This is the generalization of the existing rule above ("Keep Infra Configs
in Sync").

| Artifact | Lives in | Consumed by | Why |
|---|---|---|---|
| Healthcheck endpoint code | **Project** | Prober / orchestrator liveness | Self-Contained Projects principle |
| Prometheus metric names | **Project** | Prometheus scrape | Service owns its metric names |
| Alert rules (PromQL) | **Project** (`ops/alerts.yml`) | Prometheus (git-sync or fs mount) | When project renames a metric, breakage shows in the project's CI |
| Runbooks | **Project** (`ops/runbooks/`) | Linked from Alertmanager | Co-located with the alert |
| Dashboard definitions | **Project** (`ops/dashboards/`) | Pushed to Grafana on deploy | Project owns the definition; Grafana hosts the rendering |
| Scrape target config | Shared infra | Prometheus | The scraper's concern |
| Alertmanager routing/receivers | Shared infra | Alertmanager | Cross-project routing policy |
| Loki log shipping config | Shared infra | Loki | Backing service config |
| NGINX config | **Project** (per "Keep Infra Configs in Sync" above) | NGINX | Application routing is app knowledge |
| Tailscale ACL / network policy | Shared infra | Tailscale / firewall | Network-level, cross-project |
| Systemd unit for the service | **Project** | systemd | Service lifecycle is app knowledge |

**Why this matters for solo developers:** when you maintain both the project
and the infra repo, drift between them is invisible until something breaks.
Keeping alert rules and runbooks in the project means a rename in the code
breaks the alert in the same repo, in the same CI run. Keeping them in a
separate infra repo means the alert silently stops matching and nobody
notices for weeks.
