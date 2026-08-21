#!/usr/bin/env python3
"""Dependency-free regression tests for .env generation and validation."""

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
    assert not validate_env(path), validate_env(path)
    return dict(values)


def set_value(path: Path, key: str, value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    prefix = f"{key}="
    replaced = False
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = prefix + value
            replaced = True
            break
    assert replaced, f"missing test key {key}"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def assert_invalid(path: Path, expected_fragment: str) -> None:
    errors = validate_env(path)
    assert any(expected_fragment in error for error in errors), errors


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
        assert not validate_env(path), validate_env(path)
        assert after["PUBLIC_IP"] == "34.120.10.21"
        for key in PRESERVE_ON_UPDATE_KEYS:
            assert before[key] == after[key], f"safe update rotated {key}"

        write_fresh(path)
        set_value(path, "PUBLIC_IP", "2001:db8::1")
        assert_invalid(path, "must be an IPv4")

        write_fresh(path)
        set_value(path, "MAS_DB_NAME", "synapse")
        assert_invalid(path, "DB_NAME and MAS_DB_NAME must be different")

        write_fresh(path)
        set_value(path, "MAS_DB_USER", "synapse")
        assert_invalid(path, "DB_USER and MAS_DB_USER must be different")

        write_fresh(path)
        set_value(path, "MAS_EMAIL_REQUIRED", "sometimes")
        assert_invalid(path, "MAS_EMAIL_REQUIRED must be a boolean")

        write_fresh(path)
        set_value(path, "ELEMENT_ADMIN_IMAGE", "oci.element.io/element-admin:latest")
        assert_invalid(path, "must not use the mutable :latest tag")

        write_fresh(path)
        set_value(path, "MAS_TRUSTED_PROXIES", "10.0.0.0/8,not-a-network")
        assert_invalid(path, "MAS_TRUSTED_PROXIES contains invalid CIDR")

        write_fresh(path)
        set_value(path, "MAS_DEBUG_IMAGE", "ghcr.io/element-hq/matrix-authentication-service:1.20.0-debug")
        assert_invalid(path, "MAS_DEBUG_IMAGE must match MAS_IMAGE version")

    print("Environment safety tests passed")


if __name__ == "__main__":
    main()
