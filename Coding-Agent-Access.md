# Coding Agent Access

**Document Status:** Authoritative  
**Scope:** Filesystem, workspace, search, and indexing boundaries for coding agents  
**Applies To:** Every coding agent, IDE agent, and code-orchestration tool used with this repository, regardless of vendor, model, or product name.

This file is the project-level access contract for coding agents. It is the public source of truth.

Application runtime, local LLMs, and other models used inside the product to analyze or filter notes are not coding agents. This document does not restrict those application components.

---

## 1. Protected tree

The **production persistent-data tree** lives outside this git repository. It is out of default access for coding agents.

Coding agents must treat that entire tree as denied: knowledge sources, production databases, local model files, memory stores, caches, exports, and backups.

Do not locate, infer, reconstruct, or follow a production-data location in order to inspect it.

---

## 2. Default denial

Unless the human gives **explicit, same-request, scoped approval**, a coding agent must not:

- read, write, move, rename, or delete production persistent data;
- list or walk that tree (terminal, glob, search, or index);
- mount that tree as a workspace / project folder;
- copy production notes, vectors, or models into the git repository;
- use production databases, production embeddings, or the production knowledge vault as a scratchpad.

**Default action:** stop. Do not probe “just to check”.

---

## 3. Allowed without extra approval

- This git repository (source, tests, public docs, `Config/`)
- `tests/test_data/` and other synthetic fixtures inside the repository

---

## 4. Exception (human-approved peek)

A coding agent may touch production persistent data **only when all** of the following are true:

1. The human explicitly authorizes it in the **same** request.
2. The approval names the **specific** file or subdirectory required.
3. The agent stays inside that named scope.
4. The agent does not expand the look into adjacent production files.

Approval of one path is not approval of the data root. Absence of objection is not approval.

---

## 5. Workspace and indexing

The repository workspace must contain **only the source-code root**.

The production data root must not be added as a second workspace folder.

Editor and agent search/index should cover the repository, not the production data tree.

---

## 6. Local editor files

A developer may keep a **local, non-committed** editor-specific reminder. That file is not this contract and must not be treated as a public path catalog.

A coding agent that never loads extra editor files is still bound by this document when working on this project.

---

## 7. Local-Only Test Data

Some tests may need to reference a genuinely real, project-specific detail — the actual production data path, a real local folder name, or another machine-specific value — because there is no way to prove the relevant behavior using a synthetic value alone.

Such tests must live under `tests/local/`, which is excluded from version control via `.gitignore`. Nothing under `tests/local/` is ever pushed, shared, or exposed to anyone who clones this repository.

The bar for placing a test under `tests/local/` is narrow:

> A test belongs in `tests/local/` only if it cannot be rewritten with a synthetic/fictitious value without losing what it actually proves.

Sensitivity alone is not the criterion. A test being about security, path validation, secret detection, or any other "sensitive-sounding" topic does NOT by itself justify moving it to `tests/local/`. The default assumption is that almost every test CAN be rewritten with a synthetic value while still proving the same behavior — and when that is possible, it must stay in the public, tracked test suite.

This repository is intended to be usable by other people, on other machines, with their own data layout — not built exclusively around this developer's local environment. A test suite that only works, or only makes sense, on this specific machine defeats that goal. Prefer synthetic, portable, illustrative fixtures by default; treat `tests/local/` as the narrow exception, not a convenient place to move anything inconvenient or private-feeling.

Creating a test under `tests/local/` is never a standalone action. It
must be paired, in the same task, with a synthetic public counterpart
in the tracked suite, named per Section 8 below. Do not create a
`tests/local/` file without also creating (or confirming the existence
of) its public `.example` counterpart in the same piece of work — and
do not create a public `.example` file unless an actual real-detail
counterpart exists, or is being created right now, under
`tests/local/`. The two always come as a pair.

---

## 8. Public Example Counterpart Naming

The `.example` marker exists for exactly one purpose: to mark the
public counterpart of a test that has a real, non-synthesizable
version living in `tests/local/`. It is a *pairing* label, not a
quality label.

Do NOT apply `.example` to a test merely because it:
- uses synthetic/fake data (nearly every good test does — this is
  normal, not a special case);
- is simple, illustrative, or easy to understand;
- is "sensitive-sounding" (security, path validation, secret
  detection) but has no real counterpart in `tests/local/`.

Apply `.example` to a test ONLY when a corresponding real-detail
version of the same behavior exists (or is being created) under
`tests/local/`. If there is no local counterpart, there is no
`.example` — the test keeps its normal `test_*.py` name.

When a pairing does exist, name the public counterpart so the
pairing is obvious:

- File-level: `tests/local/test_sensitive_data_local.py` pairs with
  `tests/test_sensitive_data.example.py`.
- Function-level (same file, no rename needed): a function
  `test_machine_specific_path_detection` pairs with
  `test_machine_specific_path_detection_example`.

Before renaming anything to `.example`, explicitly identify which
`tests/local/` file it pairs with. If you cannot name that pairing,
do not apply the marker — leave the test's ordinary name alone.

---

## 9. Destructive Git Commands Require Human Approval

A coding agent must never run a destructive git command (`checkout -- <path>`, `restore`, `reset --hard`, `clean -f`, or equivalent) on any path with uncommitted changes without first showing the human the exact command and the files it would affect, and receiving explicit approval for that specific command in that specific request.

This applies even when the agent is trying to recover from its own mistake — recovering from an error is not an exception to this rule.

---

## 10. Invariant

> Coding-agent capability is not permission to access production data.  
> Minimum necessary access. Explicit scoped approval. Never the whole tree by default.
