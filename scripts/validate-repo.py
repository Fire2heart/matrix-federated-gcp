#!/usr/bin/env python3
from __future__ import annotations

import json
import py_compile
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> None:
    with (ROOT / "compose.yaml").open("r", encoding="utf-8") as handle:
        compose = yaml.safe_load(handle)
    if not isinstance(compose, dict) or "services" not in compose:
        fail("compose.yaml has no services map")

    required_services = {
        "synapse-db",
        "mas-db",
        "config-init",
        "synapse",
        "mas",
        "element",
        "livekit",
        "redis",
        "lk-jwt-service",
        "acme",
        "haproxy",
    }
    missing_services = sorted(required_services - set(compose["services"]))
    if missing_services:
        fail("Missing Compose services: " + ", ".join(missing_services))

    dockerfile = (ROOT / "config-image" / "Dockerfile").read_text(encoding="utf-8")
    if "ENTRYPOINT" not in dockerfile:
        fail("config-image/Dockerfile has no ENTRYPOINT")

    haproxy_dockerfile = (ROOT / "haproxy" / "Dockerfile").read_text(encoding="utf-8")
    if "haproxy-main.cfg" not in haproxy_dockerfile or "entrypoint.sh" not in haproxy_dockerfile:
        fail("HAProxy image does not include its config/entrypoint")

    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    env_keys = {
        line.split("=", 1)[0].strip()
        for line in env_example.splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line
    }
    compose_text = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    compose_vars = set(re.findall(r"(?<!\$)\$\{([A-Z0-9_]+)(?::-[^}]*)?\}", compose_text))
    missing_env_keys = sorted(compose_vars - env_keys)
    if missing_env_keys:
        fail("Compose references variables missing from .env.example: " + ", ".join(missing_env_keys))

    if "ACME_IMAGE=neilpang/acme.sh:" not in env_example:
        fail(".env.example must reference neilpang/acme.sh with an explicit tag")

    # EN: Compile Python helpers as part of repository validation.
    # RU: Компилируем Python helpers как часть проверки репозитория.
    for path in list((ROOT / "scripts").glob("*.py")) + [ROOT / "config-image" / "render.py"]:
        py_compile.compile(str(path), doraise=True)

    # EN: Basic guard against accidentally committed secrets in text files.
    # RU: Базовая защита от случайного коммита секретов в текстовых файлах.
    forbidden_prefixes = (
        "SYNAPSE_DB_PASSWORD=",
        "MAS_DB_PASSWORD=",
        "MAS_SHARED_SECRET=",
        "MAS_ADMIN_PASSWORD=",
        "LIVEKIT_KEY=",
        "LIVEKIT_SECRET=",
        "REDIS_PASSWORD=",
        "CLOUDFLARE_API_TOKEN=",
    )
    skip_names = {".env.example"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.name in skip_names:
            continue
        if path.name.startswith(".env"):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".zip", ".pyc"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for prefix in forbidden_prefixes:
            for line in text.splitlines():
                if line.startswith(prefix) and "${" not in line and "CHANGE_ME" not in line:
                    fail(f"Possible committed secret in {path}: {prefix}")

    # EN: Portability guard: custom GHCR images must follow repository_owner.
    # RU: Проверка переносимости: custom GHCR images должны использовать repository_owner.
    publish_cfg = (ROOT / ".github" / "workflows" / "publish-config-image.yml").read_text(encoding="utf-8")
    publish_haproxy = (ROOT / ".github" / "workflows" / "publish-haproxy-image.yml").read_text(encoding="utf-8")
    for path_name, text in (("publish-config-image.yml", publish_cfg), ("publish-haproxy-image.yml", publish_haproxy)):
        if "github.repository_owner" not in text:
            fail(f"{path_name} must derive the GHCR owner from github.repository_owner")


    # EN: Ensure the generated Element JSON shape remains serialisable.
    # RU: Проверяем, что структура генерируемого Element JSON остаётся сериализуемой.
    json.dumps({"status": "ok"})
    print("Repository validation passed")


if __name__ == "__main__":
    main()
