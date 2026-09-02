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
* Virtual environment

### Persistent Data

Persistent data is stored outside the repository and may include:

* Models
* Memory
* Databases
* Knowledge sources
* Backups

The exact location of persistent data is configured through:

```text
Config/paths.yaml
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

* `paths.yaml`
* `models.yaml`

### `paths.yaml`

Defines locations for project data and external resources.

### `models.yaml`

Defines model-related configuration.

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

## Development Notes

* Source code and persistent data should remain physically separable.
* Persistent data should not be committed to the public repository.
* Local model files should not be committed to the repository.
* Project-specific paths should be configured through `Config/paths.yaml`.
* AI models are not downloaded automatically.
* Ollama is used for local LLM inference where configured.
* Obsidian and Zotero serve as external knowledge sources.
* The development environment should remain portable across machines.
* Provider- and model-specific configuration should remain separate from the core Knowledge Management logic.
