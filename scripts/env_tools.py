#!/usr/bin/env python3
"""EN: Shared helpers for safe .env generation and validation.
RU: Общие helpers для безопасной генерации и проверки .env.
"""

from __future__ import annotations

import ipaddress
import re
import os
import secrets
import tempfile
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / ".env.example"

RANDOM_SECRET_KEYS = {
    "POSTGRES_ADMIN_PASSWORD",
    "SYNAPSE_DB_PASSWORD",
    "MAS_DB_PASSWORD",
    "MAS_SHARED_SECRET",
    "MAS_ADMIN_PASSWORD",
    "LIVEKIT_SECRET",
    "REDIS_PASSWORD",
}
PRESERVE_ON_UPDATE_KEYS = RANDOM_SECRET_KEYS | {"LIVEKIT_KEY", "CLOUDFLARE_API_TOKEN"}

DOMAIN_DERIVED_KEYS = {
    "PUBLIC_DOMAIN",
    "SYNAPSE_SERVER_NAME",
    "SYNAPSE_PUBLIC_BASEURL",
    "ELEMENT_WEB_URL",
    "MAS_PUBLIC_BASEURL",
    "LIVEKIT_PUBLIC_URL",
    "LIVEKIT_JWT_SERVICE_URL",
    "HAPROXY_MATRIX_HOST",
    "HAPROXY_MAS_HOST",
    "HAPROXY_ELEMENT_HOST",
    "HAPROXY_PANEL_HOST",
    "HAPROXY_RTC_JWT_HOST",
    "HAPROXY_RTC_HOST",
}


def parse_env(path: Path) -> tuple[OrderedDict[str, str], list[str]]:
    values: OrderedDict[str, str] = OrderedDict()
    duplicates: list[str] = []
    if not path.exists():
        return values, duplicates
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


def template_keys() -> list[str]:
    values, _ = parse_env(TEMPLATE_PATH)
    return list(values)


def random_value(key: str) -> str:
    if key == "LIVEKIT_KEY":
        return "LK" + secrets.token_hex(10)
    if key == "MAS_ADMIN_PASSWORD":
        return secrets.token_urlsafe(32)
    if key in RANDOM_SECRET_KEYS:
        return secrets.token_hex(32)
    raise KeyError(key)


def derived_values(domain: str) -> dict[str, str]:
    domain = domain.strip().lower().rstrip(".")
    return {
        "PUBLIC_DOMAIN": domain,
        "SYNAPSE_SERVER_NAME": f"matrix.{domain}",
        "SYNAPSE_PUBLIC_BASEURL": f"https://matrix.{domain}",
        "ELEMENT_WEB_URL": f"https://element.{domain}",
        "MAS_PUBLIC_BASEURL": f"https://mas.{domain}/",
        "LIVEKIT_PUBLIC_URL": f"wss://rtc.{domain}",
        "LIVEKIT_JWT_SERVICE_URL": f"https://rtc-jwt.{domain}",
        "HAPROXY_MATRIX_HOST": f"matrix.{domain}",
        "HAPROXY_MAS_HOST": f"mas.{domain}",
        "HAPROXY_ELEMENT_HOST": f"element.{domain}",
        "HAPROXY_PANEL_HOST": f"panel.{domain}",
        "HAPROXY_RTC_JWT_HOST": f"rtc-jwt.{domain}",
        "HAPROXY_RTC_HOST": f"rtc.{domain}",
    }


def render_env(
    *,
    domain: str,
    public_ip: str,
    cloudflare_zone_id: str,
    cloudflare_api_token: str,
    acme_email: str,
    admin_user: str,
    admin_display_name: str,
    existing: dict[str, str] | None = None,
    fresh: bool,
) -> str:
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    template_values, _ = parse_env(TEMPLATE_PATH)
    existing = existing or {}

    values: dict[str, str] = dict(template_values)

    # EN: Safe update preserves existing settings first, then overrides only values
    # EN: explicitly controlled by this setup operation.
    # RU: Безопасное обновление сначала сохраняет существующие настройки, а затем
    # RU: меняет только значения, которыми явно управляет текущая операция настройки.
    if not fresh:
        for key, value in existing.items():
            if key in values:
                values[key] = value

    values.update(derived_values(domain))
    values["PUBLIC_IP"] = public_ip
    values["CLOUDFLARE_ZONE_ID"] = cloudflare_zone_id
    values["ACME_EMAIL"] = acme_email
    values["MAS_ADMIN_USER"] = admin_user
    values["MAS_ADMIN_DISPLAY_NAME"] = admin_display_name

    if cloudflare_api_token:
        values["CLOUDFLARE_API_TOKEN"] = cloudflare_api_token
    elif not fresh and existing.get("CLOUDFLARE_API_TOKEN"):
        values["CLOUDFLARE_API_TOKEN"] = existing["CLOUDFLARE_API_TOKEN"]

    if fresh:
        for key in RANDOM_SECRET_KEYS | {"LIVEKIT_KEY"}:
            values[key] = random_value(key)
    else:
        # EN: Preserve persistent-service credentials during an update. Generate a value
        # EN: only when a required credential is missing or still contains a placeholder.
        # RU: При обновлении сохраняем credentials persistent-сервисов. Новое значение
        # RU: генерируется только если обязательный credential отсутствует или не заполнен.
        for key in RANDOM_SECRET_KEYS | {"LIVEKIT_KEY"}:
            current = values.get(key, "")
            if not current or current.startswith("CHANGE_ME"):
                values[key] = random_value(key)

    output_lines: list[str] = []
    for raw in template_text.splitlines():
        stripped = raw.strip()
        if stripped and not stripped.startswith("#") and "=" in raw:
            key = raw.split("=", 1)[0].strip()
            if key in values:
                output_lines.append(f"{key}={values[key]}")
                continue
        output_lines.append(raw)
    return "\n".join(output_lines) + "\n"


def validate_env(path: Path, *, allow_placeholders: set[str] | None = None) -> list[str]:
    allow_placeholders = allow_placeholders or set()
    values, duplicates = parse_env(path)
    errors: list[str] = []

    if duplicates:
        errors.append("Duplicate keys: " + ", ".join(sorted(set(duplicates))))

    required = set(template_keys())
    missing = sorted(required - set(values))
    if missing:
        errors.append("Missing keys: " + ", ".join(missing))

    for key, value in values.items():
        if "CHANGE_ME" in value and key not in allow_placeholders:
            errors.append(f"{key} still contains CHANGE_ME")

    domain = values.get("PUBLIC_DOMAIN", "").strip().lower().rstrip(".")
    if not domain or not re.fullmatch(r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", domain):
        errors.append("PUBLIC_DOMAIN is not a valid DNS domain")

    ip_value = values.get("PUBLIC_IP", "")
    try:
        ipaddress.ip_address(ip_value)
    except ValueError:
        errors.append("PUBLIC_IP is not a valid IPv4/IPv6 address")

    expected = derived_values(domain) if domain else {}
    for key in DOMAIN_DERIVED_KEYS:
        if key in expected and values.get(key) != expected[key]:
            errors.append(f"{key} does not match PUBLIC_DOMAIN ({expected[key]})")

    for key in ("SYNAPSE_PUBLIC_BASEURL", "ELEMENT_WEB_URL", "MAS_PUBLIC_BASEURL", "LIVEKIT_JWT_SERVICE_URL"):
        value = values.get(key, "")
        parsed = urlparse(value)
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"{key} must be an https:// URL")

    livekit_url = values.get("LIVEKIT_PUBLIC_URL", "")
    parsed_livekit = urlparse(livekit_url)
    if parsed_livekit.scheme != "wss" or not parsed_livekit.netloc:
        errors.append("LIVEKIT_PUBLIC_URL must be a wss:// URL")

    try:
        start = int(values.get("LIVEKIT_UDP_PORT_START", ""))
        end = int(values.get("LIVEKIT_UDP_PORT_END", ""))
        if not (1 <= start <= end <= 65535):
            raise ValueError
    except ValueError:
        errors.append("LiveKit UDP port range is invalid")

    if not values.get("ACME_IMAGE", "").startswith("neilpang/acme.sh:"):
        errors.append("ACME_IMAGE must reference neilpang/acme.sh with an explicit tag")


    return errors



def validate_env_content(content: str, *, allow_placeholders: set[str] | None = None) -> list[str]:
    """Validate rendered env text without touching the target deployment file."""
    fd, name = tempfile.mkstemp(prefix="my-matrix-env-check-", text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        return validate_env(Path(name), allow_placeholders=allow_placeholders)
    finally:
        try:
            os.unlink(name)
        except FileNotFoundError:
            pass


def write_secure_atomic(path: Path, content: str) -> None:
    """Atomically replace a local env file and keep it owner-readable only."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.chmod(0o600)
    os.replace(tmp, path)
    path.chmod(0o600)

def redact_key(key: str) -> bool:
    return key in PRESERVE_ON_UPDATE_KEYS or "PASSWORD" in key or "SECRET" in key or "TOKEN" in key
