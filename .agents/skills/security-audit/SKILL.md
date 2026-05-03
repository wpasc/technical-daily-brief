---
name: security-audit
description: >-
  Codex runtime skill generated from canonical `skills/security-audit/SKILL.md`. OWASP Top 10 audit methodology, attack surface enumeration, and vulnerability pattern detection for web applications and APIs.
---

# security-audit (Codex Runtime Skill)

Canonical source: `skills/security-audit/SKILL.md`

This file is self-contained for Codex runtime. Shared behavior belongs
in the canonical source skill; regenerate this file after changing the
source.

## Codex Runtime Notes

- Prefer `AGENTS.md` for root guidance. Treat `CLAUDE.md` only as supplemental fallback when older Claude-specific text in the inlined body requires it.
- Use Codex-native tools and `.agents/skills/`; translate older Claude coordination wording in the body into explicit user requests, current tools, or durable artifacts when the workflow requires them.

## Classification

- Migration category: Generate as Codex runtime skill
- Rationale: Workflow or reference guidance is useful in Codex as a self-contained runtime skill.

## Skill-Specific Notes

- Keep the source skill's reporting contract. In Codex, present findings first with file references, then assumptions or residual risks.

## Inlined Skill Body

## Security Audit

Offensive security methodology for code-level vulnerability discovery. Systematic
checklist-driven approach covering the OWASP Top 10, API-specific attacks, and
secret detection patterns.

---

### OWASP Top 10 Quick Reference

| # | Category | Key Tests |
|---|----------|-----------|
| A01 | Broken Access Control | IDOR, vertical escalation, CORS misconfiguration, JWT claim manipulation, forced browsing |
| A02 | Cryptographic Failures | TLS version, password hashing strength, hardcoded keys, weak PRNG |
| A03 | Injection | SQLi, NoSQLi, command injection, template injection, XSS |
| A04 | Insecure Design | Rate limiting gaps, business logic abuse, multi-step flow bypass |
| A05 | Security Misconfiguration | Default credentials, debug mode, missing security headers, directory listing |
| A06 | Vulnerable Components | Dependency CVEs, EOL libraries, known vulnerable versions |
| A07 | Auth Failures | Brute force paths, session cookie flags, session invalidation gaps, MFA bypass |
| A08 | Integrity Failures | Unsafe deserialization, missing SRI checks, CI/CD pipeline integrity |
| A09 | Logging Failures | Auth events not logged, sensitive data in logs, missing alerting |
| A10 | SSRF | Internal IP access, cloud metadata endpoints, DNS rebinding |

---

### Attack Pattern Taxonomy

#### Injection Attacks

**SQL Injection:**
- Error-based: `' OR 1=1--` in input fields
- Union-based: enumerate tables and columns via UNION SELECT
- Time-based blind: `SLEEP(5)` to confirm injection without visible output
- Boolean-based blind: true/false conditions to extract data bit by bit

**Detection patterns in code:**
- String concatenation building SQL queries
- Template literals with user input in queries
- Missing parameterized query usage
- Raw query methods with interpolated variables

**Other injection types:**
- NoSQL: `{"$gt": ""}` in MongoDB queries, `$where` with user input
- Command: user input reaching `exec()`, `system()`, `subprocess`, backticks
- Template: `{{user_input}}` in server-side template engines (Jinja2, Handlebars, EJS)
- XSS: reflected (script/img/svg payloads), stored (persistent fields), DOM-based (innerHTML + location.hash)

---

#### Authentication & Authorization

**JWT Manipulation:**
- Algorithm confusion: change `alg` to `none`, RS256-to-HS256 key confusion
- Claim modification: `role: "admin"`, `exp: 9999999999`
- Check: does the server validate the algorithm? Does it accept expired tokens?

**Session Attacks:**
- Session fixation: does session ID change after authentication?
- Cookie flags: are HttpOnly, Secure, SameSite set?
- Session invalidation: does logout actually destroy the server-side session?

**Access Control:**
- IDOR/BOLA: change resource IDs in every endpoint -- test read, update, delete across users
- BFLA: regular user tries admin endpoints (expect 403)
- Mass assignment: add privileged fields (`role`, `is_admin`) to update requests
- Privilege escalation: can horizontal access lead to vertical escalation?

---

#### API-Specific Attacks

**Rate Limiting:**
- Rapid-fire requests to auth endpoints -- expect 429 after threshold
- Check if rate limiting applies per-user, per-IP, or globally
- Test bypass via header manipulation (X-Forwarded-For)

**GraphQL:**
- Introspection: should be disabled in production
- Query depth attacks: deeply nested queries causing resource exhaustion
- Batch mutations: bypassing rate limits via batched operations
- Field suggestion: information disclosure via error messages

**SSRF:**
- Internal IP access (127.0.0.1, 10.x, 172.16.x, 192.168.x)
- Cloud metadata: AWS `169.254.169.254`, GCP, Azure equivalents
- Bypass techniques: IPv6, hex encoding, decimal encoding, DNS rebinding

---

#### Secret Detection Patterns

Scan code, config, and git history for:

| Pattern | Examples |
|---------|---------|
| API keys | `AKIA...` (AWS), `AIza...` (Google), `sk-...` (OpenAI/Stripe) |
| Tokens | Bearer tokens, OAuth tokens, JWT secrets in code |
| Passwords | `password =`, `passwd`, `pwd`, `secret` assignments |
| Private keys | `-----BEGIN RSA PRIVATE KEY-----`, `-----BEGIN EC PRIVATE KEY-----` |
| Connection strings | `postgres://user:pass@`, `mongodb://`, `redis://` with credentials |
| Env file commits | `.env` files in git history, even if later removed |

**Where secrets hide:**
- Hardcoded in source (obvious)
- In comments ("temporary" credentials)
- In test fixtures (real credentials used for testing)
- In error messages and logs (leaked at runtime)
- In git history (removed from HEAD but still in commits)

---

### CVE Triage Workflow

1. **Collect** -- run ecosystem audit tools, aggregate findings
2. **Deduplicate** -- group by CVE ID across direct and transitive deps
3. **Prioritize** -- severity + exploitability + reachability = fix priority
   - Critical + exploitable + reachable = fix immediately
   - Critical + not reachable = verify unreachability, then schedule
   - Low + exploitable = monitor, may compound with other findings
4. **Remediate** -- upgrade, patch, or apply compensating controls
5. **Verify** -- rerun audit to confirm fix, update lock files

---

### Audit Process

#### Step 1: Map Trust Boundaries

Identify every point where data crosses a trust boundary:
- User input (forms, query params, headers, cookies, file uploads)
- API calls (inbound and outbound)
- Database queries
- File system access
- Environment variables and configuration
- Inter-service communication

#### Step 2: Trace Data Flow

For each trust boundary, trace data from entry to use:
- Is input validated at the boundary?
- Is output sanitized before rendering?
- Is the principle of least privilege followed?
- Are error messages generic (not leaking internals)?

#### Step 3: Check Authentication & Authorization

- Every endpoint: does it require authentication? Should it?
- Every data access: does it check authorization for the requesting user?
- Session management: creation, validation, invalidation, timeout
- Password storage: hashing algorithm, salt, iteration count

#### Step 4: Review Configuration

- Debug/development flags in production code paths
- Default credentials or passwords
- Overly permissive CORS, CSP, or security headers
- Exposed admin interfaces or internal endpoints

---

### Anti-Patterns

| Anti-Pattern | Why It Matters |
|-------------|---------------|
| Relying solely on automated tools | Tools miss business logic flaws, chained exploits, and novel vectors |
| Ignoring low-severity findings | A chain of lows can become a critical exploit path |
| Reporting without remediation | Every finding must include actionable fix guidance |
| Testing only happy paths | Attackers never use the happy path |
| Trusting client-side validation | Client-side checks are UX, not security |
| Security through obscurity | Hidden endpoints, obfuscated parameters are not access control |
