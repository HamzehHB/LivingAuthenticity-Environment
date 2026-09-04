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

## 7. Invariant

> Coding-agent capability is not permission to access production data.  
> Minimum necessary access. Explicit scoped approval. Never the whole tree by default.
