"""Validate that the Prior Labs / TabPFN API key is available locally.

Do not commit API keys to GitHub.

Run from the repository root:

    cp .env.example .env
    # paste PRIORLABS_API_KEY in .env
    python scripts/02_validate_priorlabs_env.py

This script only validates local environment configuration. The actual API
request flow will be added after the WHO analytical dataset is built.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def mask_secret(value: str) -> str:
    if len(value) <= 10:
        return "*" * len(value)
    return f"{value[:6]}...{value[-4:]}"


def main() -> None:
    api_key = os.getenv("PRIORLABS_API_KEY", "").strip()

    if not api_key:
        raise SystemExit(
            "PRIORLABS_API_KEY was not found. Create a local .env file from .env.example and add the key there."
        )

    print("Prior Labs API key found locally.")
    print(f"Masked key: {mask_secret(api_key)}")
    print("No secret was written to disk or committed to GitHub.")


if __name__ == "__main__":
    main()
