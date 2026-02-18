"""
Phase 1 — Clarifier Agent

Asks the user clarifying questions about their game idea.
Loops until the LLM decides the requirements are clear.
Returns a consolidated requirements summary.
"""

import os
from openai import OpenAI


# Sentinel the LLM uses to signal "requirements are clear"
_READY_TAG = "REQUIREMENTS_CLEAR"


def _load_system_prompt() -> str:
    """Load the clarifier system prompt from the prompts/ directory."""
    prompt_path = os.path.join(
        os.path.dirname(__file__), "..", "prompts", "clarifier_prompt.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def run(client: OpenAI, model: str, game_idea: str) -> str:
    """
    Run the clarification loop.

    Args:
        client:    An initialised OpenAI client.
        model:     The model name to use.
        game_idea: The user's raw game idea in natural language.

    Returns:
        A consolidated string summarising the clarified requirements.
    """
    system_prompt = _load_system_prompt()

    # Conversation history keeps context across turns
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"My game idea: {game_idea}"},
    ]

    print("\n" + "=" * 60)
    print("PHASE 1 — REQUIREMENTS CLARIFICATION")
    print("=" * 60)
    print("The agent will ask you a few questions to understand your idea.\n")

    while True:
        # Ask the LLM for questions (or a "ready" signal)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
        )
        assistant_msg = response.choices[0].message.content.strip()

        # Check if the LLM signals that requirements are clear
        if _READY_TAG in assistant_msg:
            # Extract the summary between <summary> tags
            summary = _extract_summary(assistant_msg)
            print("\n✅  Requirements are clear!")
            print(f"\n📋  Summary:\n{summary}\n")
            return summary

        # Otherwise, show the questions and get user answers
        print(f"🤖  Agent:\n{assistant_msg}\n")
        messages.append({"role": "assistant", "content": assistant_msg})

        user_answer = input("👤  Your answer: ").strip()
        if not user_answer:
            user_answer = "No preference, use your best judgment."
        messages.append({"role": "user", "content": user_answer})
        print()


def _extract_summary(text: str) -> str:
    """Pull the summary from between <summary>...</summary> tags."""
    start = text.find("<summary>")
    end = text.find("</summary>")
    if start != -1 and end != -1:
        return text[start + len("<summary>") : end].strip()
    # Fallback: return everything after the READY tag
    idx = text.find(_READY_TAG)
    return text[idx + len(_READY_TAG) :].strip()
