# Security — LivingAuthenticity Environment

**Status:** Authoritative — operational security baseline
**Role:** The per-checkpoint security routine and the verified security state
of this repository. It grants no access and introduces no rules; principles and
authority live in [AI-Governance.md](AI-Governance.md), filesystem and data
access in [Coding-Agent-Access.md](Coding-Agent-Access.md), and the current
implementation boundary in `.project/Current-Summer-Scope.md`.

---

## 1. Current Security Posture (verified)

Facts verified against the repository at this checkpoint:

* No secrets, credentials, API keys, tokens, or private keys exist in any
  tracked file or anywhere in git history (pattern scan against the known
  pattern list in `src/living_authenticity/security/sensitive_data.py` —
  zero matches).
* Git history **does** contain historical machine-specific filesystem paths
  (former `Config/paths.yaml` versions and an older workspace file). This is a
  documented residual risk (§5). No history rewriting is performed by agents.
* Application code performs no network calls, no dynamic code execution
  (`eval`/`exec`), no shell-out (`subprocess`/`os.system`), and no
  deserialization of untrusted data.
* The analytical pipeline is analysis-only: it performs no authoritative writes
  to knowledge. The single controlled-execution boundary
  (`knowledge/governance/execution/`) writes exactly one approved + revalidated
  `CREATE` artifact (`<proposal_hash>.md`) into an explicitly supplied
  staging root confined by `PathBoundary`, with no overwrite and no
  authoritative-vault placement. Current executable action scope is
  `CREATE` / `DO_NOT_IMPORT` / `NEEDS_REVIEW` — everything else is future work.
* Private configuration and private documents are physically outside the
  tracked tree: `Config/paths.local.yaml`, `.project/`, `.clinerules/`,
  `Venv/`, `.env`, and `Logs/*` are all covered by `.gitignore` and verified
  with `git check-ignore`. `Config/paths.local.yaml` must **never be committed
  or pushed**.
* The production persistent-data tree is **denied to coding agents by
  default**. Runtime data-processing components follow
  `.project/Local-Paths-Reference.md`; that access never extends to
  development agents, and knowing a path is not permission.
* Reusable runtime security utilities live in `src/living_authenticity/security/`: a default-deny path boundary (`PathBoundary`) and value-safe sensitive-data detection (`find_secrets` / `contains_secret`). `PathBoundary` is wired into the controlled-execution boundary (`knowledge/governance/execution/`) as its staging confinement; it remains unwired into the ingestion/analysis pipeline, which performs no writes.

---

## 2. Per-Checkpoint Security Checklist (run before every commit)

Steps 1–5 are automated in `tests/test_repository_security.py` — keep it green:

1. **Secret scan** — no known secret patterns in tracked files.
2. **Machine-path scan** — the configured production data root and the
   repository's own machine path appear in no tracked file (the actual root
   is defined only in `Config/paths.local.yaml`; synthetic test fixtures use
   invented values).
3. **Ignore rules** — `.gitignore` covers `Config/paths.local.yaml`,
   `.project/`, `.clinerules/`, `Venv/`, `.env`, `Logs/`, and
   `git check-ignore` confirms every one of them.
4. **Policy alignment** — this file exists and stays consistent with
   `AI-Governance.md` and `Coding-Agent-Access.md`.
5. **Unsafe-code scan** — no `subprocess`, `os.system`, `eval`, `exec`,
   `__import__`, `shell=True`, or `pickle` in application code.

Then, manually per checkpoint:

6. **Dependency sync** — `requirements*.in` match the imports actually used
   (see §4); compiled files regenerated; test suite green.
7. **Diff review** — `git diff --check` clean; `git status` contains only the
   files this checkpoint claims to change.

---

## 3. Dependency Security

* Workflow: `requirements.in → requirements.txt` and
  `requirements-dev.in → requirements-dev.txt`, compiled with pip-tools.
* `.in` manifests list only dependencies that are **directly imported** by the
  code today. Nothing is added speculatively for possible future use.
* `pip-tools` itself is a development tool: it lives in `requirements-dev.in`,
  not in the runtime manifest.
* A new dependency may be added only by the checkpoint that actually needs it,
  with a one-line justification in that checkpoint's report.

---

## 4. Incident Response (private project)

* Report suspected vulnerabilities **privately to the maintainer** — never in
  public issues, and never with secrets, private paths, or production data in
  the report.
* Exposed secret → revoke/rotate it immediately, then assess exposure. Removing
  material from git history is a maintainer decision; agents never rewrite
  history.
* Production data exposed to an unauthorized actor → determine the scope of
  exposure, stop all processing that touches it, and request human review.

---

## 5. Residual Risks (accepted, maintainer-owned)

* Historical machine-specific paths in git history (see §1). Accepted: they
  reveal a folder layout, not credentials; rewriting history is a
  maintainer-only decision.
* Maintainer actions on GitHub (outside the repository): enable secret scanning
  and push protection; consider branch protection for `main`.
