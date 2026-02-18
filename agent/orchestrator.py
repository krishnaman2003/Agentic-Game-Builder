"""
Orchestrator — Main control flow for the Game-Builder Agent.

Enforces strict phase ordering: Clarify → Plan → Execute.
Each phase is a separate module with its own LLM system prompt.
"""

import os
from openai import OpenAI
from agent import clarifier, planner, builder




def run(client: OpenAI, model: str, game_idea: str, output_dir: str) -> list[str]:
    """
    Run the full agent pipeline: Clarify → Plan → Execute.

    Args:
        client:     An initialised OpenAI client.
        model:      The model name to use.
        game_idea:  The user's raw game idea.
        output_dir: Where to write the generated game files.

    Returns:
        A list of created file paths.
    """
    print("\n" + "🚀" * 20)
    print("  AGENTIC GAME-BUILDER AI")
    print("🚀" * 20)
    print(f"\n📝  Game Idea: {game_idea}")

    # ── Phase 1: Clarify ─────────────────────────────────────
    requirements = clarifier.run(client, model, game_idea)

    # ── Phase 2: Plan ─────────────────────────────────────────
    plan = planner.run(client, model, requirements)

    # ── Phase 3: Build ────────────────────────────────────────
    created_files = builder.run(client, model, plan, output_dir)

    # ── Done ──────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("🎉  ALL DONE!")
    print("=" * 60)
    print(f"Open {os.path.join(output_dir, 'index.html')} in your browser to play!")
    print()

    return created_files
