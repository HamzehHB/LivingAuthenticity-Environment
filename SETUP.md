# LivingAuthenticity Environment — Development Setup

This document describes the local development environment and the basic requirements for running the **LivingAuthenticity Environment**.

## Python

* Python 3.13+

## External Software

The following software should be installed before running the project:

* Git
* Visual Studio Code
* Ollama
* Obsidian
* Zotero

## Models

### Embedding Model

* BGE-M3

### Local LLM

* Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf

Models are not downloaded automatically by the project. They must already exist in the configured model directories.

---

## Project Layout

The project separates **source code** from **persistent data**.

### Source Code

The repository contains:

* Source code
* Configuration
* Documentation
* Prompts
* Tests
* Development logs

The local development environment may also contain a virtual
environment (`Venv/`), which is not part of the repository.

### Persistent Data

Persistent data is stored outside the repository and may include:

* Models
* Memory
* Databases
* Knowledge sources
* Backups

The exact location of persistent data is configured through:

```text
Config/paths.local.yaml
```

which you create from the committed template:

```text
Config/paths.example.yaml
```

This allows the project to remain independent of a specific machine or drive layout.

---

## Installation

### Create a virtual environment

```bash
python -m venv Venv
```

### Activate the virtual environment

#### Windows

```powershell
Venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Data Structure

The persistent data environment is organized conceptually into the following areas:

```text
Models/
Memory/
Knowledge/
Database/
Backups/
```

### Models

Contains:

* Embedding models
* Local LLMs

### Memory

Contains the project's persistent memory layers, where applicable:

* conversations
* episodic
* semantic
* reflection
* identity
* goals
* values
* working

### Knowledge

Contains external and structured research knowledge, including:

* Obsidian
* Zotero
* Exports

### Database

Contains database-related data such as:

* Cache
* Embeddings
* Vector databases

---

## Configuration

Configuration files are stored in:

```text
Config/
```

Current configuration files include:

* `paths.example.yaml`
* `paths.local.yaml`
* `models.yaml`

### `paths.example.yaml`

The committed configuration template. It contains only generic,
portable placeholder values and defines the contract for a valid
paths configuration. It never contains real machine-specific values.

### `paths.local.yaml`

The real, machine-specific configuration for your computer.
It is ignored by git and must never be committed or pushed.

### `models.yaml`

Committed, machine-independent model settings (for example the
active embedding model and its dimension).

### Configuration workflow

1. Copy the template:

   ```bash
   cp Config/paths.example.yaml Config/paths.local.yaml
   ```

2. Edit `Config/paths.local.yaml` and set the real locations for
   your machine (persistent data root, model path, vector database,
   Obsidian vault, Zotero library, exports, and cache).

3. Run the test suite (see Testing) to verify your configuration
   loads correctly.

Repository-internal locations — the repository root itself and the
`Logs` and `Prompts` directories — are always derived automatically
from the repository root. They must not be set in
`paths.example.yaml` or `paths.local.yaml`.

If `Config/paths.local.yaml` is missing, the loader falls back to the
generic values in `paths.example.yaml`. These values are placeholders
and should be replaced with machine-specific paths before using
persistent data.

---

## Dependency Management

The project uses **pip-tools** for dependency management.

### Source dependencies

```text
requirements.in
```

### Resolved dependencies

```text
requirements.txt
```

### Regenerate dependencies

```bash
pip-compile requirements.in
```

## Testing

The project uses **pytest**. Dev-only dependencies are managed with
pip-tools separately from the runtime dependencies:

```text
requirements-dev.in
requirements-dev.txt
```

Install the dev dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the full test suite from the repository root:

```bash
python -m pytest
```

The tests run against the real `Config/` directory for the
integration check and against synthetic temporary configurations for
everything else. No production data is read by the test suite.

---

## Private Project Documents

Some project documents are intentionally kept local and are not committed to the public repository.

They are stored under:

```text
.project/
```

This directory may contain:

* `Project-Vision.md`
* `Current-Summer-Scope.md`

The `.project/` directory is excluded through `.gitignore`.

---

## Coding Agent Access

Coding agents (Cursor, Codex, Claude Code, and others) must not access the production persistent-data tree by default.

The canonical contract is:

```text
Coding-Agent-Access.md
```

The development workspace should open only the source-code repository, not the persistent data root.

---

## Development Notes

* Source code and persistent data should remain physically separable.
* Persistent data should not be committed to the public repository.
* Local model files should not be committed to the repository.
* Project-specific paths should be configured through
  `Config/paths.local.yaml`, created from `Config/paths.example.yaml`.
* AI models are not downloaded automatically.
* Ollama is used for local LLM inference where configured.
* Obsidian and Zotero serve as external knowledge sources.
* The development environment should remain portable across machines.
* Provider- and model-specific configuration should remain separate from the core Knowledge Management logic.
