# 🎮 Agentic Game-Builder AI

An agentic AI system that accepts a natural-language game idea, asks clarifying questions, produces a structured internal plan, and generates a fully playable HTML/CSS/JavaScript game — all without any hard-coded templates or manual editing.

**Powered by open-source LLMs running locally via [Ollama](https://ollama.com/) — no API costs, fully private.**

---

## Agent Architecture

The system is built around a strict **three-phase pipeline** enforced by a central orchestrator. Each phase is a separate Python module with its own dedicated LLM system prompt. Phases cannot be skipped or merged.

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  Orchestrator  (agent/orchestrator.py)              │
│  Enforces: Clarify → Plan → Build                   │
└──────────┬──────────────┬──────────────┬────────────┘
           │              │              │
           ▼              ▼              ▼
    Phase 1          Phase 2        Phase 3
   Clarifier         Planner        Builder
(clarifier.py)   (planner.py)   (builder.py)
           │              │              │
           ▼              ▼              ▼
    User Q&A       JSON Game Plan   index.html
                                    style.css
                                    game.js
```

### Phase 1 — Requirements Clarification (`agent/clarifier.py`)

The clarifier receives the user's raw game idea and enters a conversation loop with the LLM. The LLM asks 2–4 focused questions per turn about genre, controls, win/lose conditions, and visual style. The user answers interactively. The loop continues until the LLM is confident the requirements are clear, at which point it emits a `REQUIREMENTS_CLEAR` sentinel tag followed by a consolidated requirements summary. This summary is passed to Phase 2.

### Phase 2 — Planning (`agent/planner.py`)

The planner receives the requirements summary and instructs the LLM to produce a **structured JSON game plan**. The plan includes:

- `game_title`, `framework` (always `vanilla_js`)
- `mechanics` — list of core gameplay rules
- `controls` — key bindings and input description
- `game_loop` — init, update, render, win condition, lose condition
- `entities` — list of game objects
- `visual_style` — brief description
- `core_systems` — input handling, rendering, state management
- `file_structure` — description of each output file

The JSON is parsed and validated before being passed to Phase 3.

### Phase 3 — Code Generation (`agent/builder.py`)

The builder receives the JSON plan and instructs the LLM to generate three complete files using strict delimiters:

```
===FILE: index.html===
...
===END FILE===

===FILE: style.css===
...
===END FILE===

===FILE: game.js===
...
===END FILE===
```

The builder parses these blocks with a regex, validates all three files are present, and writes them to the output directory. The result is a playable game that runs by opening `index.html` in any browser.

### LLM Backend

The agent uses the **OpenAI Python SDK** as its HTTP client, but points it at **Ollama's OpenAI-compatible endpoint** (`/v1/chat/completions`). This means:

- No OpenAI API key required
- Any model available in Ollama can be used
- Switching models requires only a single line change in `.env`

### System Prompts (`prompts/`)

Each phase has a dedicated plain-text system prompt file. These are loaded at runtime — not embedded in code — making them easy to tune independently without touching any Python files.

---

## Project Structure

```
Game-Builder-AI/
├── agent/
│   ├── __init__.py          # Package init
│   ├── orchestrator.py      # Phase sequencing and control flow
│   ├── clarifier.py         # Phase 1: interactive requirements loop
│   ├── planner.py           # Phase 2: structured JSON game plan
│   └── builder.py           # Phase 3: game file generation
├── prompts/
│   ├── clarifier_prompt.txt # System prompt for Phase 1
│   ├── planner_prompt.txt   # System prompt for Phase 2
│   └── builder_prompt.txt   # System prompt for Phase 3
├── output/                  # Generated game files land here
├── main.py                  # CLI entry point
├── requirements.txt         # Python dependencies (openai, python-dotenv)
├── Dockerfile               # Docker packaging
├── .dockerignore
├── .env.example             # Config template — copy to .env
├── .gitignore
└── README.md
```

---

## Prerequisites

### 1. Install Ollama

Download and install from [https://ollama.com](https://ollama.com), then start the server:

```bash
ollama serve
```

### 2. Pull a Model

The agent works with any Ollama model. Recommended options:

```bash
# Best quality (~20 GB, needs 16 GB+ VRAM or 32 GB+ RAM)
ollama pull qwen2.5-coder:32b

# Good balance of quality and speed (~4.7 GB)
ollama pull qwen2.5-coder:7b

# Lightweight option (~1 GB)
ollama pull qwen2.5-coder:1.5b
```

### 3. Verify

```bash
ollama list    # Should show your pulled model
```

---

## How to Run Locally

```bash
# 1. Clone the repository
git clone <repo-url>
cd Game-Builder-AI

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure the model
cp .env.example .env
# Open .env and set LLM_MODEL to your pulled model name

# 5. Run the agent (Ollama must be running)
python main.py
```

The agent will:
1. Validate Ollama is reachable and the model is available
2. Prompt you for a game idea (or use `--idea`)
3. Run Phase 1 → Phase 2 → Phase 3
4. Write `index.html`, `style.css`, and `game.js` to `./output/`

Open `output/index.html` in any browser to play the generated game.

### CLI Options

| Flag | Description |
|------|-------------|
| `--idea "..."` | Pass the game idea directly (skips the interactive prompt) |
| `--model <name>` | Override `LLM_MODEL` from `.env` for this run |
| `--output <dir>` | Write game files to a custom directory (default: `./output`) |

### Configuration (`.env`)

```env
# Ollama server URL (default works for local installs)
OLLAMA_BASE_URL=http://localhost:11434/v1

# Ollama does not require a real API key — leave as-is
OLLAMA_API_KEY=ollama

# Model to use — must be pulled in Ollama first
# Change this line to switch models; no code changes needed
LLM_MODEL=qwen2.5-coder:32b
```

Changing `LLM_MODEL` is all that is needed to switch models. The agent validates the model is available before starting and prints a clear error with the exact `ollama pull` command if it is not.

---

## Docker Build & Run

> **Important:** The Docker container connects to an Ollama server running on your **host machine**. Start Ollama on your host before running the container.

### Build

```bash
docker build -t game-builder .
```

### Run (Interactive)

```bash
# Linux / Mac
docker run -it \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434/v1 \
  -e LLM_MODEL=qwen2.5-coder:32b \
  -v $(pwd)/output:/app/output \
  game-builder

# Windows (PowerShell)
docker run -it `
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434/v1 `
  -e LLM_MODEL=qwen2.5-coder:32b `
  -v ${PWD}/output:/app/output `
  game-builder
```

### Run (With Idea Pre-Set)

```bash
docker run -it \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434/v1 \
  -e LLM_MODEL=qwen2.5-coder:32b \
  -v $(pwd)/output:/app/output \
  game-builder --idea "A snake game where the snake grows on eating food"
```

Generated files appear in `./output/` on the host via the volume mount. Open `output/index.html` in a browser to play.

---

## Dependencies

```
openai>=1.0.0        # Used as the HTTP client for Ollama's OpenAI-compatible API
python-dotenv>=1.0.0 # Loads .env configuration at startup
```

No other external libraries are required. The generated games use only browser-native APIs (HTML5 Canvas, `requestAnimationFrame`).

---
