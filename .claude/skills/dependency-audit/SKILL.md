---
name: dependency-audit
description: >-
  Dependency vulnerability scanning, supply chain risk assessment, bloat
  detection, and upgrade path analysis across multi-language manifests.
  TRIGGER when: adding new dependencies, reviewing dependency changes in PRs,
  auditing existing dependency manifests, evaluating supply chain security,
  or when dependency-related security concerns arise.
  DO NOT TRIGGER when: writing application code that uses existing dependencies,
  configuring build tools, or running a full red team (use red-team which
  composes with this skill).
user-invocable: false
---

# Dependency Audit

Systematic analysis of project dependencies for security vulnerabilities, supply
chain risk, bloat, and upgrade hygiene. Multi-language support across all major
package ecosystems.

---

## Supported Ecosystems

| Language | Manifest Files | Lockfiles |
|----------|---------------|-----------|
| JavaScript/Node.js | package.json | package-lock.json, yarn.lock, pnpm-lock.yaml |
| Python | requirements.txt, pyproject.toml, Pipfile | Pipfile.lock, poetry.lock, uv.lock |
| Go | go.mod | go.sum |
| Rust | Cargo.toml | Cargo.lock |
| Ruby | Gemfile | Gemfile.lock |
| Java/Maven | pom.xml | gradle.lockfile |
| PHP | composer.json | composer.lock |
| C#/.NET | packages.config | project.assets.json |

---

## Vulnerability Scanning

### CVE Matching

For each dependency, check:
- Direct CVE matches against the declared version
- Transitive dependency vulnerabilities (deps of deps)
- CVSS scoring: severity (low/medium/high/critical) + exploitability + reachability

### Prioritization Matrix

| Severity | Exploitable | Reachable | Action |
|----------|-------------|-----------|--------|
| Critical | Yes | Yes | Fix immediately |
| Critical | Yes | No | Verify unreachability, schedule fix |
| Critical | No | Yes | Schedule fix, monitor advisories |
| High | Yes | Yes | Fix in current sprint |
| High | No | No | Schedule in next cycle |
| Medium/Low | Any | Any | Track, batch with other updates |

### Triage Workflow

1. **Collect** -- identify all manifest and lockfiles, enumerate full dependency tree
2. **Deduplicate** -- group findings by CVE ID across direct and transitive paths
3. **Prioritize** -- apply the matrix above
4. **Remediate** -- upgrade, patch, or apply compensating controls
5. **Verify** -- confirm fix resolved the CVE, update lockfiles

---

## Bloat Detection

### Unused Dependencies

Identify declared dependencies that aren't actually imported:
- Compare import/require statements against manifest declarations
- Flag deps only used in removed or commented-out code
- Identify dev dependencies bundled in production

### Oversized Packages

Flag dependencies where the functionality used doesn't justify the package size:
- Using a large utility library for one function (e.g., all of lodash for `_.get`)
- Framework-level packages imported for a single component
- Packages with large native binaries when pure-JS alternatives exist

### Redundant Dependencies

- Multiple packages providing the same functionality (e.g., moment + dayjs + date-fns)
- Dependencies that duplicate functionality already in the language standard library
- Transitive version conflicts (multiple versions of the same package in the tree)

---

## Supply Chain Risk

### Provenance Verification

- Are packages sourced from official registries?
- Do lockfiles include integrity hashes?
- Are package signatures verified?

### Maintainer Risk

- Recent maintainer ownership changes (account compromise risk)
- Single-maintainer packages for critical functionality
- Packages with no releases in 12+ months (abandoned)
- Sudden spike in new contributors (potential compromise)

### Typosquatting Detection

- Package names similar to popular packages (e.g., `colours` vs `colors`)
- Recently published packages mimicking established ones
- Packages with minimal documentation but high install counts

### Transitive Depth

- How deep is the dependency tree? Deep trees = more attack surface
- Are there circular dependencies?
- What percentage of the tree is transitive vs. direct?

---

## Lockfile Validation

- Lockfile exists and is committed to version control
- Lockfile is in sync with manifest (no drift)
- Integrity hashes are present and valid
- No resolved URLs pointing to unexpected registries
- Deterministic resolution (same result on any machine)

---

## Upgrade Risk Assessment

| Risk Level | Criteria | Approach |
|-----------|----------|----------|
| Low | Patch versions, security fixes only | Auto-merge with CI passing |
| Medium | Minor versions, new features, no breaking changes | Review changelog, test, merge |
| High | Major versions, API changes, deprecations | Dedicated upgrade task, migration plan |
| Critical | Breaking changes with no migration path, EOL | Evaluate alternatives, plan replacement |

### Upgrade Prioritization

1. Security patches (highest -- fix known vulnerabilities)
2. Bug fixes (high -- resolve known issues)
3. Feature updates (medium -- evaluate benefit vs. risk)
4. Major rewrites (planned -- dedicated migration effort)
5. Deprecated packages (immediate attention -- plan replacement)

---

## Audit Process

### Step 1: Inventory

- Locate all manifest and lockfiles in the repository
- Enumerate the full dependency tree (direct + transitive)
- Note the total dependency count and tree depth

### Step 2: Security Scan

- Check each dependency version against known CVEs
- Identify transitive vulnerabilities
- Apply the prioritization matrix
- Document findings with CVE IDs and affected paths

### Step 3: Bloat Analysis

- Compare declared deps against actual imports
- Flag unused, oversized, and redundant packages
- Calculate approximate bundle/install size impact

### Step 4: Supply Chain Review

- Check maintainer status and activity
- Verify package provenance and integrity
- Scan for typosquatting risk
- Assess transitive depth and complexity

### Step 5: Lockfile Health

- Validate lockfile existence, sync, and integrity
- Check for unexpected registry URLs
- Verify deterministic resolution

---

## Anti-Patterns

| Anti-Pattern | Why It Matters |
|-------------|---------------|
| No lockfile committed | Non-deterministic builds, supply chain risk |
| Floating version specifiers (`*`, `latest`) | Builds break unpredictably, auto-ingest vulnerabilities |
| Ignoring transitive vulnerabilities | "It's not my direct dep" -- attackers don't care about your dependency graph |
| Dev deps in production | Larger attack surface, slower builds, unnecessary exposure |
| One-time audit then forget | Dependencies change daily; scanning must be continuous |
| Updating everything at once | Big-bang upgrades hide which change broke things |
