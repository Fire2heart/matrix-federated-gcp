#!/usr/bin/env python3
"""Small dependency-free regression tests for .env safety logic."""

from __future__ import annotations

import tempfile
from pathlib import Path

from env_tools import PRESERVE_ON_UPDATE_KEYS, parse_env, render_env, validate_env

ZONE = "0123456789abcdef0123456789abcdef"


def write_fresh(path: Path) -> dict[str, str]:
    content = render_env(
        domain="example.com",
        public_ip="34.120.10.20",
        cloudflare_zone_id=ZONE,
        cloudflare_api_token="test-token",
        acme_email="ci@example.com",
        admin_user="admin",
        admin_display_name="Administrator",
        existing={},
        fresh=True,
    )
    path.write_text(content, encoding="utf-8")
    values, _ = parse_env(path)
    assert not validate_env(path)
    return values


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / ".env"
        before = write_fresh(path)

        updated_content = render_env(
            domain="example.com",
                public_ip="34.120.10.21",
            cloudflare_zone_id=before["CLOUDFLARE_ZONE_ID"],
            cloudflare_api_token="",
            acme_email=before["ACME_EMAIL"],
            admin_user=before["MAS_ADMIN_USER"],
            admin_display_name=before["MAS_ADMIN_DISPLAY_NAME"],
            existing=before,
            fresh=False,
        )
        path.write_text(updated_content, encoding="utf-8")
        after, _ = parse_env(path)
        assert not validate_env(path)
        assert after["PUBLIC_IP"] == "34.120.10.21"
        for key in PRESERVE_ON_UPDATE_KEYS:
            assert before[key] == after[key], f"safe update rotated {key}"

    print("Environment safety tests passed")


if __name__ == "__main__":
    main()
