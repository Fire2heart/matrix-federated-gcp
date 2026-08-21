#!/usr/bin/env python3
"""EN: Validate a matrix-federated-gcp .env without printing secret values.
RU: Проверяет matrix-federated-gcp .env, не выводя секретные значения.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from env_tools import ROOT, parse_env, validate_env


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate matrix-federated-gcp .env without revealing secrets")
    parser.add_argument("env_file", nargs="?", default=".env")
    parser.add_argument(
        "--allow-placeholder",
        action="append",
        default=[],
        help="Key allowed to contain CHANGE_ME (CI use only; may be repeated)",
    )
    args = parser.parse_args()

    path = Path(args.env_file)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        print(f"[ERROR] File not found: {path}")
        return 2

    values, duplicates = parse_env(path)
    errors = validate_env(path, allow_placeholders=set(args.allow_placeholder))

    print(f"Checking {path}")
    print(f"[OK] Parsed {len(values)} environment variables")
    if not duplicates:
        print("[OK] No duplicate keys")
    if not any("CHANGE_ME" in value for key, value in values.items() if key not in args.allow_placeholder):
        print("[OK] No unresolved CHANGE_ME values")

    if errors:
        print("\nValidation failed:")
        for error in errors:
            print(f"[ERROR] {error}")
        return 1

    print("[OK] Domain-derived URLs/hostnames are consistent")
    print("[OK] Network, image and service-specific values are valid")
    print("[OK] Environment is ready for Docker Compose")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
