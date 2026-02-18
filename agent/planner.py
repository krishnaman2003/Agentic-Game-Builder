"""
Phase 2 — Planner Agent

Takes clarified requirements and produces a structured game plan in JSON.
"""

import json
import os
from openai import OpenAI


def _load_system_prompt() -> str:
    """Load the planner system prompt from the prompts/ directory."""
    prompt_path = os.path.join(
        os.path.dirname(__file__), "..", "prompts", "planner_prompt.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def run(client: OpenAI, model: str, requirements: str) -> dict:
    """
    Generate a structured game plan from clarified requirements.

    Args:
        client:       An initialised OpenAI client.
        model:        The model name to use.
        requirements: The consolidated requirements summary from Phase 1.

    Returns:
        A dict containing the structured game plan.
    """
    system_prompt = _load_system_prompt()

    print("\n" + "=" * 60)
    print("PHASE 2 — PLANNING")
    print("=" * 60)
    print("Generating a structured game plan...\n")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Here are the clarified game requirements:\n\n{requirements}",
            },
        ],
        temperature=0.4,
    )

    raw = response.choices[0].message.content.strip()

    # Try to parse JSON from the response
    plan = _parse_json(raw)

    print("✅  Game plan created!")
    print(f"\n📋  Plan Overview:")
    print(f"    Title:     {plan.get('game_title', 'Untitled')}")
    print(f"    Framework: {plan.get('framework', 'vanilla_js')}")
    print(f"    Mechanics: {', '.join(plan.get('mechanics', []))}")
    print(f"    Controls:  {plan.get('controls', {}).get('description', 'N/A')}")
    print()

    return plan


def _parse_json(text: str) -> dict:
    """
    Extract and parse JSON from the LLM response.
    Handles cases where the JSON is wrapped in markdown code fences.
    """
    # Strip markdown code fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Remove first line (```json) and last line (```)
        lines = cleaned.split("\n")
        lines = lines[1:]  # remove opening fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]  # remove closing fence
        cleaned = "\n".join(lines)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Last resort: try to find JSON between { and }
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
        raise ValueError(f"Could not parse JSON from LLM response:\n{text}")
