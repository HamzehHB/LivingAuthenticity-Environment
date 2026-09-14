LivingAuthenticity Environment

![Monica](Monica.jpg)
*Just Monica felt right in this place.*
[For Monica](https://hamzehhb3.substack.com/p/for-monica)

«A modular research infrastructure for organizing, retrieving, and developing knowledge with AI assistance.»

The LivingAuthenticity Environment is a long-term research infrastructure designed to support the organization, processing, retrieval, and development of personal and research knowledge.

The project is built around a simple principle:

«AI assists the research process; the researcher remains the authority.»

Architecture

- [AI Governance](AI-Governance.md) — authority boundaries, permissions, and human approval.
- [Knowledge Schema](Knowledge-Schema.yaml) — the canonical knowledge representation schema.
- [Coding Agent Access](Coding-Agent-Access.md) — filesystem and data-access boundaries.

Current Status

The project is currently focused on building its foundational infrastructure.

Implemented foundations include:

- Python project and package structure
- Centralized configuration and path management
- Text ingestion and parsing foundation
- Semantic chunking
- Dependency management
- Testing infrastructure
- Project documentation and governance
- Separation of source code from persistent data
- Deterministic analytical stages (classification, retrieval,
  comparison, relation detection, core analysis, proposal,
  confidence) plus a proposed Obsidian note representation
  (Generated Note ≠ Authoritative Note; representation does not
  execute CREATE)

Advanced components such as semantic retrieval, embeddings, LanceDB, knowledge evolution, and agent systems belong to later development phases and are not represented as completed features.

Technology

The current foundation is built primarily with Python.

LanceDB and BGE-M3 are retained as planned components of the future architecture.

Configuration

Machine-specific configuration is kept outside the public repository through:

`Config/paths.local.yaml`

The committed [Config/paths.example.yaml](Config/paths.example.yaml) provides a portable template.

See [SETUP.md](SETUP.md) for development setup, configuration, dependencies, and testing.

Testing

Install the dev dependencies ([requirements-dev.txt](requirements-dev.txt)) and run the test suite:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Tests use synthetic fixtures and temporary configurations only.

Direction

The long-term direction is to evolve from reliable infrastructure toward a research environment supporting:

Knowledge → Retrieval → Reasoning → Research → Knowledge Evolution

while remaining model-, provider-, and agent-independent.

Status

This project is under active development.