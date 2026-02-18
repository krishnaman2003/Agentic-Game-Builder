"""
main.py — Entry point for the Agentic Game-Builder AI.

Model and backend are fully configured via the .env file.
No values are hardcoded — update .env to switch models.

Usage:
    python main.py
    python main.py --idea "A snake game with power-ups"
    python main.py --model qwen2.5-coder:7b
"""

import argparse
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

from agent import orchestrator


def _check_ollama(client: OpenAI, base_url: str) -> None:
    """
    Verify that the Ollama server is reachable and the requested model is available.
    Exits with a helpful message if either check fails.
    """
    try:
        models = client.models.list()
        available = [m.id for m in models.data]
    except Exception as e:
        print(f"\n❌  Cannot reach Ollama at: {base_url}")
        print("    Make sure Ollama is running:  ollama serve")
        print(f"    Error: {e}")
        sys.exit(1)
    return available


def main():
    # ── Load .env first — all config lives there ──────────────
    load_dotenv()

    # ── Read config from environment (set in .env) ─────────────
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    api_key         = os.getenv("OLLAMA_API_KEY", "ollama")
    env_model       = os.getenv("LLM_MODEL")          # No hardcoded fallback

    # ── CLI arguments (override .env values if provided) ───────
    parser = argparse.ArgumentParser(
        description="Agentic Game-Builder AI — generate playable HTML games from ideas"
    )
    parser.add_argument(
        "--idea",
        type=str,
        default=None,
        help="Your game idea in natural language (prompted interactively if omitted)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,   # None means "use .env value"
        help="Ollama model to use. Overrides LLM_MODEL in .env.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "output"),
        help="Directory to write generated game files (default: ./output)",
    )
    args = parser.parse_args()

    # CLI --model flag takes priority; fall back to .env LLM_MODEL
    model = args.model or env_model

    # If neither is set, tell the user exactly what to do
    if not model:
        print("\n❌  No model specified.")
        print("    Set LLM_MODEL in your .env file, for example:")
        print("        LLM_MODEL=qwen2.5-coder:32b")
        print("    Or pass it via CLI:  python main.py --model qwen2.5-coder:7b")
        sys.exit(1)

    # ── Create OpenAI-compatible client pointing at Ollama ─────
    client = OpenAI(base_url=ollama_base_url, api_key=api_key)

    # ── Validate Ollama is reachable and model is pulled ───────
    available_models = _check_ollama(client, ollama_base_url)
    if model not in available_models:
        print(f"\n❌  Model '{model}' is not available in Ollama.")
        print(f"    Pull it first:  ollama pull {model}")
        print(f"    Available models: {', '.join(available_models) or 'none'}")
        sys.exit(1)

    # ── Get game idea ───────────────────────────────────────────
    game_idea = args.idea
    if not game_idea:
        print("\n🎮  Welcome to the Agentic Game-Builder AI!")
        print("─" * 50)
        print(f"   Model  : {model}")
        print(f"   Backend: {ollama_base_url}")
        print("─" * 50)
        game_idea = input("Enter your game idea: ").strip()
        if not game_idea:
            print("❌  Error: No game idea provided.")
            sys.exit(1)

    # ── Run the agent pipeline ─────────────────────────────────
    orchestrator.run(client, model, game_idea, args.output)


if __name__ == "__main__":
    main()

