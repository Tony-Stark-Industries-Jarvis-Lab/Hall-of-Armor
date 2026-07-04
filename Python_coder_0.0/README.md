# Stark Industries — Multi-Agent HQ

> A local multi-agent system powered by Ollama, with a pixel-art web interface and a vibe-coding pipeline.

## Project Map

| Path | Purpose |
|---|---|
| [app.py](app.py) | Core agent routing, Ollama HTTP client, and the vibe-coding pipeline. |
| [server.py](server.py) | Flask app exposing the web UI, SSE chat endpoint, and file-plan application endpoint. |
| [static/index.html](static/index.html) | Main browser UI with the office layout, chat terminal, and editor modal. |
| [static/style.css](static/style.css) | Pixel-art styling, workstation states, and modal styling. |
| [static/main.js](static/main.js) | Front-end controller for streaming, routing animations, and editor actions. |
| [asset office/](asset%20office/) | Sprite sheets and workstation characters used by the interface. |
| [jeu_juste_prix/main.py](jeu_juste_prix/main.py) | Small standalone CLI game entry point. |
| [jeu_juste_prix/utils.py](jeu_juste_prix/utils.py) | Game logic for the "Guess the Price" mini-game. |
| [environment.yml](environment.yml) | Conda environment specification for the project. |
| [requirements.txt](requirements.txt) | Legacy dependency list kept for reference; Conda is the supported install path. |

## Overview

Stark Industries orchestrates several local LLM agents through a retro office-themed UI. Each agent is visualized as a workstation character. Requests are routed automatically to the best agent, or they trigger a collaborative development pipeline when code generation is requested.

**Stack:** Python 3.11 · Flask 3 · Ollama local server · Vanilla JavaScript · CSS pixel art

## Agents

### Standard agents

| Agent | Role |
|---|---|
| Code Expert | Answers programming questions and debugs code. |
| General Expert | Handles general-purpose questions outside programming. |
| Writer Expert | Produces structured text and saves it to `outputs/`. |

The router analyzes the request and delegates it to the most appropriate agent. It uses the same Ollama host as the rest of the application.

### Code Team pipeline

When the request asks to create or implement code, the Code Team pipeline is used:

```text
User request
    -> Architect
    -> Developer
    -> Reviewer
    -> Tester
    -> Architect final validation
    -> Editor
```

Each step streams live into the UI. The Editor generates a file plan that the user can review before writing anything to disk.

## Installation

### 1. Create the Conda environment

From the project root, create the local environment in the repository folder:

```bash
conda env create -p ./SI_1 -f environment.yml
```

### 2. Activate it

```bash
conda activate ./SI_1
```

If your shell does not accept the relative prefix, activate it with the absolute path instead:

```bash
conda activate "/Users/seb/Programmation/Collab Guillaume/Stark_industries/SI_1"
```

### 3. Install and run Ollama itself

The Python project uses the Ollama HTTP API, so the Ollama application or daemon must be installed separately on macOS or Linux and left running locally.

Pull the models used by the project:

```bash
ollama pull qwen2.5-coder:1.5b
```

### 4. Launch the web app

```bash
python server.py
```

Then open http://127.0.0.1:5000.

## Configuration

The default model settings live in [app.py](app.py):

```python
MODEL = "qwen2.5-coder:1.5b"
OLLAMA_HOST = "http://127.0.0.1:11434"

_PIPELINE_MODELS = {
    "developpeur": MODEL,
    "reviseur": MODEL,
    "testeur": MODEL,
    "editeur": MODEL,
}
```

## macOS / Linux compatibility notes

- The old Windows-only virtualenv activation (`.venv\Scripts\activate`) has been replaced with Conda commands that work on macOS and Linux.
- The project now uses the Ollama HTTP API directly, so no Python `ollama` package installation is required.
- The [jeu_juste_prix/main.py](jeu_juste_prix/main.py) entry point previously contained an invalid leading `python` token; it has been removed so the script runs normally on Unix-like systems.
- Paths containing spaces, such as `asset office/`, should be quoted when used in shell commands.
- If you add new shell examples, prefer `Path` in Python or quoted POSIX paths so they stay portable.

## Dependencies

The Conda environment includes the runtime dependency needed by the project:

- Python 3.11
- Flask 3.x

The Ollama client is accessed over HTTP, so the only external requirement is a running local Ollama service with the requested models already pulled.

## How To Use the Agents

1. Start the Ollama service locally and make sure the models are available.
2. Launch the app with `python server.py`, then open the web interface in your browser.
3. Type a question in the terminal input at the bottom of the page.
4. Ask for programming help to reach the Code Expert, ask for general questions for the General Expert, and ask for writing tasks when you want the Writer Expert.
5. When you want to generate new code, describe the feature or app you want to build; the request will go through the Code Team pipeline automatically.
6. If the Editor proposes files, review the plan in the modal and choose an action for each file before applying it.
7. Watch the workstation lights and the terminal stream to follow which agent is active and what it is doing.
