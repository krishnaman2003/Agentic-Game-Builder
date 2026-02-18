"""
Phase 3 — Builder Agent

Takes a structured game plan and generates three files:
  - index.html
  - style.css
  - game.js

Writes them to the output/ directory.
"""

import json
import os
import re
from openai import OpenAI


# Regex to match ===FILE: <name>=== ... ===END FILE===
_FILE_PATTERN = re.compile(
    r"===FILE:\s*(.+?)===\s*\n(.*?)===END FILE===",
    re.DOTALL,
)


def _load_system_prompt() -> str:
    """Load the builder system prompt from the prompts/ directory."""
    prompt_path = os.path.join(
        os.path.dirname(__file__), "..", "prompts", "builder_prompt.txt"
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def run(client: OpenAI, model: str, plan: dict, output_dir: str) -> list[str]:
    """
    Generate game files from the structured plan.

    Args:
        client:     An initialised OpenAI client.
        model:      The model name to use.
        plan:       The structured game plan dict from Phase 2.
        output_dir: Directory to write the generated files to.

    Returns:
        A list of file paths that were created.
    """
    system_prompt = _load_system_prompt()

    print("\n" + "=" * 60)
    print("PHASE 3 — CODE GENERATION")
    print("=" * 60)
    print("Generating game files...\n")

    plan_json = json.dumps(plan, indent=2)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Here is the game plan. Generate the three files:\n\n{plan_json}",
            },
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    raw = response.choices[0].message.content.strip()

    # Parse the three files from the response
    files = _parse_files(raw)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    created = []
    for filename, content in files.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        created.append(filepath)
        print(f"   ✅  Written: {filename}")

    print(f"\n🎮  Game files generated in: {output_dir}")
    return created


def _parse_files(text: str) -> dict[str, str]:
    """
    Extract file contents from the LLM response using the
    ===FILE: name=== ... ===END FILE=== delimiters.
    """
    matches = _FILE_PATTERN.findall(text)

    if not matches:
        raise ValueError(
            "Could not parse file blocks from LLM response.\n"
            "Expected format: ===FILE: filename=== ... ===END FILE==="
        )

    files = {}
    for name, content in matches:
        filename = name.strip()
        files[filename] = content.strip() + "\n"

    # Verify we got all three expected files
    expected = {"index.html", "style.css", "game.js"}
    missing = expected - set(files.keys())
    if missing:
        raise ValueError(f"Missing expected files in LLM output: {missing}")

    return files
