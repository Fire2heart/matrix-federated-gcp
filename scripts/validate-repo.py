#!/usr/bin/env python3
"""Static repository validation for the current deployment architecture."""

from __future__ import annotations

import py_compile
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = {
    ".env.example",
    ".github/workflows/validate.yml",
    "compose.yaml",
    "config-image/Dockerfile",
    "config-image/render.py",
    "haproxy/Dockerfile",
    "haproxy/entrypoint.sh",
    "haproxy/haproxy-main.cfg",
    "postgres/init-databases.sh",
    "scripts/check-env.py",
    "scripts/env_tools.py",
    "scripts/generate-env.py",
    "scripts/setup-env.py",
    "scripts/smoke-test.sh",
    "scripts/test-env-tools.py",
    "requirements-dev.txt",
}

REQUIRED_SERVICES = {
    "postgres",
    "config-init",
    "synapse",
    "mas",
    "element",
    "element-admin",
    "livekit",
    "redis",
    "lk-jwt-service",
    "bootstrap-admin",
    "acme",
    "haproxy",
}

IMAGE_ENV_KEYS = {
    "ACME_IMAGE",
    "POSTGRES_IMAGE",
    "REDIS_IMAGE",
    "SYNAPSE_IMAGE",
    "MAS_IMAGE",
    "MAS_DEBUG_IMAGE",
    "ELEMENT_WEB_IMAGE",
    "ELEMENT_ADMIN_IMAGE",
    "LIVEKIT_IMAGE",
    "LK_JWT_IMAGE",
    "HAPROXY_BASE_IMAGE",
}


def fail(message: str) -> None:
    raise RuntimeError(message)


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a YAML mapping")
    return value


def parse_env_template(path: Path) -> tuple[dict[str, str], list[str]]:
    values: dict[str, str] = {}
    duplicates: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in values:
            duplicates.append(key)
        values[key] = value
    return values, duplicates


def require_build(service: dict, *, context: str, args: dict[str, str]) -> None:
    build = service.get("build")
    if not isinstance(build, dict) or build.get("context") != context:
        fail(f"Service build context must be {context}")
    actual_args = build.get("args") or {}
    if not isinstance(actual_args, dict):
        fail(f"Build args for {context} must be a mapping")
    for key, expected in args.items():
        if actual_args.get(key) != expected:
            fail(f"Build arg {key} for {context} must be {expected}")


def require_depends_on(service_name: str, service: dict, dependency: str) -> None:
    depends_on = service.get("depends_on") or {}
    if dependency not in depends_on:
        fail(f"Service {service_name} must depend on {dependency}")


def has_explicit_image_ref(value: str) -> bool:
    if "@sha256:" in value:
        return True
    return ":" in value.rsplit("/", 1)[-1]


def main() -> None:
    missing_files = sorted(path for path in REQUIRED_FILES if not (ROOT / path).is_file())
    if missing_files:
        fail("Missing required files: " + ", ".join(missing_files))

    compose = load_yaml(ROOT / "compose.yaml")
    if compose.get("name") != "${COMPOSE_PROJECT_NAME}":
        fail("compose.yaml project name must come from COMPOSE_PROJECT_NAME")

    services = compose.get("services")
    if not isinstance(services, dict):
        fail("compose.yaml has no services map")

    missing_services = sorted(REQUIRED_SERVICES - set(services))
    if missing_services:
        fail("Missing Compose services: " + ", ".join(missing_services))

    postgres_services = [
        name for name, service in services.items() if service.get("image") == "${POSTGRES_IMAGE}"
    ]
    if postgres_services != ["postgres"]:
        fail("The deployment must use exactly one PostgreSQL service named postgres")

    postgres_volumes = services["postgres"].get("volumes") or []
    if "postgres_data:/var/lib/postgresql/data" not in postgres_volumes:
        fail("postgres must persist data in postgres_data")
    if "./postgres/init-databases.sh:/docker-entrypoint-initdb.d/10-matrix-databases.sh:ro" not in postgres_volumes:
        fail("postgres must mount postgres/init-databases.sh read-only")

    require_build(
        services["config-init"],
        context="./config-image",
        args={
            "SYNAPSE_IMAGE": "${SYNAPSE_IMAGE}",
            "MAS_IMAGE": "${MAS_IMAGE}",
        },
    )
    if "image" in services["config-init"]:
        fail("config-init must be built locally rather than pulled as a project-owned image")

    require_build(
        services["haproxy"],
        context="./haproxy",
        args={"HAPROXY_BASE_IMAGE": "${HAPROXY_BASE_IMAGE}"},
    )
    if "image" in services["haproxy"]:
        fail("haproxy must be built locally rather than pulled as a project-owned image")

    require_depends_on("synapse", services["synapse"], "postgres")
    require_depends_on("mas", services["mas"], "postgres")

    bootstrap = services["bootstrap-admin"]

    if bootstrap.get("user") != "0:0":
        fail("bootstrap-admin must run as root so it can write its one-shot marker")

    bootstrap_command = "\n".join(bootstrap.get("command") or [])

    if "http://mas:8081/health" not in bootstrap_command:
        fail("bootstrap-admin must wait for the MAS internal health listener")

    if "--username" in bootstrap_command:
        fail("bootstrap-admin must use the positional username syntax required by MAS 1.21.0")

    if '"$${MAS_ADMIN_USER}"' not in bootstrap_command:
        fail("bootstrap-admin must pass MAS_ADMIN_USER as the positional register-user argument")

    volumes = compose.get("volumes") or {}
    if "postgres_data" not in volumes:
        fail("compose.yaml must declare postgres_data")

    env_values, env_duplicates = parse_env_template(ROOT / ".env.example")
    if env_duplicates:
        fail("Duplicate .env.example keys: " + ", ".join(sorted(set(env_duplicates))))

    compose_text = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    compose_vars = set(re.findall(r"(?<!\$)\$\{([A-Z0-9_]+)(?::-[^}]*)?\}", compose_text))
    missing_env_keys = sorted(compose_vars - set(env_values))
    if missing_env_keys:
        fail("Compose references variables missing from .env.example: " + ", ".join(missing_env_keys))

    missing_image_keys = sorted(IMAGE_ENV_KEYS - set(env_values))
    if missing_image_keys:
        fail("Missing image variables in .env.example: " + ", ".join(missing_image_keys))
    for key in sorted(IMAGE_ENV_KEYS):
        value = env_values[key]
        if not has_explicit_image_ref(value):
            fail(f"{key} must use an explicit image tag or digest")
        if value.rsplit(":", 1)[-1] == "latest":
            fail(f"{key} must not use :latest")

    mas_image = env_values.get("MAS_IMAGE", "")
    if "@" not in mas_image and env_values.get("MAS_DEBUG_IMAGE") != mas_image + "-debug":
        fail("MAS_DEBUG_IMAGE must match MAS_IMAGE with the -debug suffix")

    config_dockerfile = (ROOT / "config-image" / "Dockerfile").read_text(encoding="utf-8")
    for arg in ("SYNAPSE_IMAGE", "MAS_IMAGE"):
        if not re.search(rf"^ARG {arg}\s*$", config_dockerfile, flags=re.MULTILINE):
            fail(f"config-image/Dockerfile must declare ARG {arg} without a default")

    haproxy_dockerfile = (ROOT / "haproxy" / "Dockerfile").read_text(encoding="utf-8")
    if not re.search(r"^ARG HAPROXY_BASE_IMAGE\s*$", haproxy_dockerfile, flags=re.MULTILINE):
        fail("haproxy/Dockerfile must declare ARG HAPROXY_BASE_IMAGE without a default")
    if "haproxy-main.cfg" not in haproxy_dockerfile or "entrypoint.sh" not in haproxy_dockerfile:
        fail("HAProxy image must include its config and entrypoint")

    haproxy_config = (ROOT / "haproxy" / "haproxy-main.cfg").read_text(encoding="utf-8")
    if "option httpchk GET /healthz" not in haproxy_config:
        fail("HAProxy rtc_jwt backend must use the /healthz application health check")

    postgres_init = (ROOT / "postgres" / "init-databases.sh").read_text(encoding="utf-8")
    for token in ("SYNAPSE_DB_USER", "SYNAPSE_DB_NAME", "MAS_DB_USER", "MAS_DB_NAME", "CREATE DATABASE"):
        if token not in postgres_init:
            fail(f"PostgreSQL init script is missing {token}")

    for path in list((ROOT / "scripts").glob("*.py")) + [ROOT / "config-image" / "render.py"]:
        py_compile.compile(str(path), doraise=True)

    # EN: Guard against accidentally committed deployment secrets in ordinary text files.
    # RU: Защита от случайно закоммиченных deployment-секретов в обычных текстовых файлах.
    forbidden_prefixes = (
        "POSTGRES_ADMIN_PASSWORD=",
        "SYNAPSE_DB_PASSWORD=",
        "MAS_DB_PASSWORD=",
        "MAS_SHARED_SECRET=",
        "MAS_ADMIN_PASSWORD=",
        "LIVEKIT_KEY=",
        "LIVEKIT_SECRET=",
        "REDIS_PASSWORD=",
        "CLOUDFLARE_API_TOKEN=",
    )
    ignored_parts = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in ignored_parts for part in path.parts):
            continue
        if path.name == ".env.example" or path.name.startswith(".env"):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".zip", ".pyc"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            for prefix in forbidden_prefixes:
                if line.startswith(prefix) and "${" not in line and "CHANGE_ME" not in line:
                    fail(f"Possible committed secret in {path.relative_to(ROOT)}: {prefix}")

    print("Repository validation passed")


if __name__ == "__main__":
    main()
