# LivingAuthenticity-AI Development Setup

## Python

- Python 3.13+

---

## External Software

The following software must be installed before running the project:

- Git
- Visual Studio Code
- Ollama
- Obsidian
- Zotero

---

## Installed Models

### Embedding Models

- BGE-M3

### Local LLMs

- Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf

---

## Project Layout

The project is intentionally separated into two independent locations.

### Source Code

```
E:\LivingAuthenticity_AI
```

Contains:

- Source code
- Configuration
- Documentation
- Prompts
- Logs
- Virtual Environment

---

### Persistent Data

```
F:\LivingAuthenticity_Data
```

Contains:

- Models
- Memory
- Databases
- Knowledge Sources
- Backups

---

## Installation

### Create a virtual environment

```bash
python -m venv Venv
```

### Activate the virtual environment

Windows

```bash
Venv\Scripts\activate
```

### Install project dependencies

```bash
pip install -r requirements.txt
```

---

## Data Structure

### Models

```
F:\LivingAuthenticity_Data\Models
```

Contains:

- Embedding_Model
- Local_LLM

---

### Memory

```
F:\LivingAuthenticity_Data\Memory
```

Contains:

- conversations
- episodic
- semantic
- reflection
- identity
- goals
- values
- working

---

### Knowledge

```
F:\LivingAuthenticity_Data\Knowledge
```

Contains:

- Obsidian
- Zotero
- Exports

---

### Database

```
F:\LivingAuthenticity_Data\Database
```

Contains:

- Cache
- Embedding
- Vector_Database

---

## Configuration

Configuration files are stored in:

```
Config/
```

Current configuration:

- paths.yaml
- models.yaml

---

## Dependency Management

This project uses **pip-tools**.

Main dependencies:

```
requirements.in
```

Resolved dependencies:

```
requirements.txt
```

Regenerate dependencies:

```bash
pip-compile requirements.in
```

---

## Notes

- Source code is stored on the SSD for maximum performance.
- Persistent data is stored on the HDD for capacity and long-term storage.
- Project paths are configured in `Config/paths.yaml`.
- AI models are **not downloaded automatically** and must already exist in the configured model directories.
- Ollama is used for local LLM inference.
- Obsidian and Zotero are integrated as external knowledge sources.
- The project is designed to keep source code and persistent data physically separated.