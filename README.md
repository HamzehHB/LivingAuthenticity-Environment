# LivingAuthenticity Environment

The **LivingAuthenticity Environment** is the infrastructure for my research ecosystem.

It is a modular environment for working with research knowledge, supporting **RAG, knowledge ingestion, semantic search, and structured note organization**.

## Architecture

* [AI Governance](AI-Governance.md) — principles, authority boundaries, and rules governing AI-assisted operations.
* [Knowledge Schema](Knowledge-Schema.yaml) — the canonical schema for knowledge representation and management.
* [Coding Agent Access](Coding-Agent-Access.md) — project-level filesystem boundary for coding agents versus production data.

## Technology

The current technical foundation is built primarily with **Python**, with **LanceDB** and **BGE-M3** retained as planned/frozen components of the architecture.

## Configuration

Configuration lives in `Config/` and is loaded by a single central
loader (`Config/settings.py`):

* `paths.example.yaml` — the committed configuration template with
  generic, portable placeholder values.
* `paths.local.yaml` — your real machine-specific configuration.
  Create it by copying the template; it is ignored by git and must
  **never be committed or pushed**.
* `models.yaml` — committed, machine-independent model settings.

Repository-internal locations (the repository root, `Logs/` and
`Prompts/`) are derived automatically from the repository root.

See [SETUP.md](SETUP.md) for the full setup and configuration workflow.

## Testing

The test suite runs with **pytest** from the repository root:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Tests use synthetic fixtures and temporary configurations only; they
never read production data.

## Direction

The long-term direction is to develop an environment where research knowledge can be organized, connected, retrieved, evaluated, and evolved with AI assistance, while keeping human judgment and authority at the center.

> **AI assists the research process; the researcher remains the authority.**

## Status

This project is under active development.
