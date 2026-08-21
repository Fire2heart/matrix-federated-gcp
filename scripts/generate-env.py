#!/usr/bin/env python3
"""EN: Non-interactive .env generator.
RU: Неинтерактивный генератор .env.

EN: Interactive deployments should use scripts/setup-env.py. This command is intended
EN: for CI and non-interactive automation.
RU: Для интерактивной установки используйте scripts/setup-env.py. Эта команда предназначена
RU: для CI и неинтерактивной автоматизации.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from env_tools import ROOT, parse_env, render_env, validate_env_content, write_secure_atomic


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a matrix-federated-gcp .env safely. For interactive setup use scripts/setup-env.py."
    )
    parser.add_argument("--domain", required=True)
    parser.add_argument(
        "--public-ip",
        dest="public_ip",
        required=True,
        help="Static public IPv4 address assigned to the GCP VM and advertised by LiveKit",
    )
    parser.add_argument("--cloudflare-zone-id")
    parser.add_argument(
        "--cloudflare-api-token",
        default="",
        help="Intended for CI only. For real secrets prefer setup-env.py so the token is not stored in shell history.",
    )
    parser.add_argument("--acme-email")
    parser.add_argument("--admin-user")
    parser.add_argument("--admin-display-name")
    parser.add_argument("--output", default=".env")
    parser.add_argument(
        "--preserve-from",
        help="Existing .env whose settings/secrets should be preserved. Use this for an existing installation.",
    )
    parser.add_argument(
        "--force-new",
        action="store_true",
        help="Allow overwriting output with newly generated persistent-service secrets. Destructive for existing volumes.",
    )
    args = parser.parse_args()

    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output

    preserve_path: Path | None = None
    if args.preserve_from:
        preserve_path = Path(args.preserve_from)
        if not preserve_path.is_absolute():
            preserve_path = ROOT / preserve_path
        if not preserve_path.exists():
            parser.error(f"--preserve-from file does not exist: {preserve_path}")

    if output.exists() and not preserve_path and not args.force_new:
        print(
            f"Cannot overwrite existing {output} without an explicit update or fresh-install mode.\n"
            "A fresh .env rotates database/MAS/Redis/LiveKit secrets and can break existing volumes.\n"
            "For an existing installation use:\n"
            f"  python3 scripts/generate-env.py ... --preserve-from {output.name} --output {output.name}\n"
            "Or use the safer interactive wizard:\n"
            "  python3 scripts/setup-env.py",
            file=sys.stderr,
        )
        return 2

    existing: dict[str, str] = {}
    fresh = preserve_path is None
    if preserve_path:
        existing, _ = parse_env(preserve_path)

    cloudflare_zone_id = args.cloudflare_zone_id or existing.get(
        "CLOUDFLARE_ZONE_ID", "CHANGE_ME_CLOUDFLARE_ZONE_ID"
    )
    acme_email = args.acme_email if args.acme_email is not None else existing.get("ACME_EMAIL", "")
    admin_user = args.admin_user or existing.get("MAS_ADMIN_USER", "admin")
    admin_display_name = args.admin_display_name or existing.get(
        "MAS_ADMIN_DISPLAY_NAME", "Administrator"
    )

    content = render_env(
        domain=args.domain,
        public_ip=args.public_ip,
        cloudflare_zone_id=cloudflare_zone_id,
        cloudflare_api_token=args.cloudflare_api_token,
        acme_email=acme_email,
        admin_user=admin_user,
        admin_display_name=admin_display_name,
        existing=existing,
        fresh=fresh,
    )
    allowed = set()
    if not args.cloudflare_api_token:
        allowed.add("CLOUDFLARE_API_TOKEN")
    if cloudflare_zone_id.startswith("CHANGE_ME"):
        allowed.add("CLOUDFLARE_ZONE_ID")
    errors = validate_env_content(content, allow_placeholders=allowed)
    if errors:
        print("Refusing to write an invalid environment file:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    write_secure_atomic(output, content)
    print(f"Created {output}")
    if fresh:
        print("Mode: FRESH INSTALL — new persistent-service secrets were generated.")
    else:
        print(f"Mode: SAFE UPDATE — existing settings/secrets were preserved from {preserve_path}.")
    print("Environment validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
