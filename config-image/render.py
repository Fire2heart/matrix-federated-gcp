#!/usr/bin/env python3
"""EN: Generate persistent runtime configuration for the my_matrix stack.
RU: Генерирует постоянные runtime-конфиги для стека my_matrix.

EN: This image is intentionally the only place where configuration rendering lives.
EN: The Compose file describes services; this script describes their configuration.
RU: Рендеринг конфигурации намеренно сосредоточен в этом image.
RU: Compose описывает сервисы, а этот скрипт описывает их конфигурацию.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

import yaml


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable {name} is empty")
    return value


def optional(name: str, default: str) -> str:
    value = os.environ.get(name, "").strip()
    return value or default


def as_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be true or false, got {raw!r}")


def comma_list(name: str, default: str) -> list[str]:
    raw = optional(name, default)
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if not values:
        raise RuntimeError(f"{name} resolved to an empty list")
    return values


def write_yaml(path: Path, data: object, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)
    path.chmod(mode)


def write_json(path: Path, data: object, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    path.chmod(mode)


def generate_synapse() -> None:
    data_dir = Path("/data")
    config_path = data_dir / "homeserver.yaml"
    data_dir.mkdir(parents=True, exist_ok=True)

    server_name = required("SYNAPSE_SERVER_NAME")
    public_base = required("SYNAPSE_PUBLIC_BASEURL").rstrip("/") + "/"
    element_url = required("ELEMENT_WEB_URL").rstrip("/") + "/"
    mas_url = required("MAS_PUBLIC_BASEURL").rstrip("/") + "/"
    jwt_url = required("LIVEKIT_JWT_SERVICE_URL").rstrip("/")

    report_stats = as_bool("SYNAPSE_REPORT_STATS", False)
    if not config_path.exists():
        print("[config-init] Generating initial Synapse configuration")
        env = os.environ.copy()
        env["SYNAPSE_CONFIG_PATH"] = str(config_path)
        env["SYNAPSE_SERVER_NAME"] = server_name
        env["SYNAPSE_REPORT_STATS"] = "yes" if report_stats else "no"
        subprocess.run(["/start.py", "generate"], env=env, check=True)

    with config_path.open("r", encoding="utf-8") as handle:
        cfg = yaml.safe_load(handle) or {}

    existing_name = cfg.get("server_name")
    if existing_name and existing_name != server_name:
        raise RuntimeError(
            f"Refusing to change Synapse server_name from {existing_name!r} "
            f"to {server_name!r}. Recreate volumes for a clean deployment."
        )

    cfg["server_name"] = server_name
    cfg["public_baseurl"] = public_base
    cfg["web_client_location"] = element_url
    cfg["report_stats"] = report_stats

    cfg["serve_server_wellknown"] = True
    cfg["extra_well_known_client_content"] = {
        "org.matrix.msc2965.authentication": {
            "issuer": mas_url,
            "account": mas_url + "account/",
        },
        "org.matrix.msc4143.rtc_foci": [
            {
                "type": "livekit",
                "livekit_service_url": jwt_url,
            }
        ],
    }

    cfg["matrix_authentication_service"] = {
        "enabled": True,
        "endpoint": "http://mas:8080/",
        "secret": required("MAS_SHARED_SECRET"),
    }

    # EN: Registration is owned by MAS, not Synapse.
    # RU: Регистрацией управляет MAS, а не Synapse.
    cfg["enable_registration"] = False
    cfg["enable_registration_without_verification"] = False
    cfg.pop("registration_shared_secret", None)
    cfg.pop("registration_requires_token", None)

    experimental = cfg.get("experimental_features") or {}
    experimental.pop("msc3861", None)
    experimental.pop("msc3266_enabled", None)  # stable in current Synapse
    experimental["msc4222_enabled"] = True
    cfg["experimental_features"] = experimental

    cfg["user_directory"] = {
        "enabled": True,
        "search_all_users": as_bool("USER_DIRECTORY_SEARCH_ALL", True),
        "prefer_local_users": True,
        "exclude_remote_users": as_bool("USER_DIRECTORY_EXCLUDE_REMOTE", True),
        "show_locked_users": False,
    }

    cfg["max_event_delay_duration"] = "24h"
    cfg["rc_message"] = {"per_second": 0.5, "burst_count": 30}
    cfg["rc_delayed_event_mgmt"] = {"per_second": 1, "burst_count": 20}

    # Federation is a core feature of this deployment and is always enabled.
    resources = ["client", "federation"]

    cfg["listeners"] = [
        {
            "port": 8008,
            "tls": False,
            "type": "http",
            "x_forwarded": True,
            "bind_addresses": ["0.0.0.0"],
            "resources": [{"names": resources, "compress": False}],
        }
    ]

    cfg["database"] = {
        "name": "psycopg2",
        "args": {
            "user": required("SYNAPSE_DB_USER"),
            "password": required("SYNAPSE_DB_PASSWORD"),
            "database": required("SYNAPSE_DB_NAME"),
            "host": "postgres",
            "port": 5432,
            "cp_min": 5,
            "cp_max": 10,
        },
    }

    write_yaml(config_path, cfg)
    print("[config-init] Synapse configuration ready")


def generate_mas() -> None:
    config_dir = Path("/generated/mas")
    config_path = config_dir / "mas.yaml"
    config_dir.mkdir(parents=True, exist_ok=True)

    if not config_path.exists() or config_path.stat().st_size == 0:
        print("[config-init] Generating persistent MAS keys and base configuration")
        with config_path.open("wb") as output:
            subprocess.run(
                ["/usr/local/bin/mas-cli", "config", "generate"],
                stdout=output,
                check=True,
            )

    with config_path.open("r", encoding="utf-8") as handle:
        cfg = yaml.safe_load(handle) or {}

    mas_base = required("MAS_PUBLIC_BASEURL").rstrip("/") + "/"
    db_user = required("MAS_DB_USER")
    db_password = required("MAS_DB_PASSWORD")
    db_name = required("MAS_DB_NAME")
    db_uri = (
        "postgresql://"
        + quote(db_user, safe="")
        + ":"
        + quote(db_password, safe="")
        + "@postgres:5432/"
        + quote(db_name, safe="")
        + "?sslmode=disable"
    )

    cfg.setdefault("http", {})
    cfg["http"]["public_base"] = mas_base
    cfg["http"]["issuer"] = mas_base
    cfg["http"]["trusted_proxies"] = comma_list(
        "MAS_TRUSTED_PROXIES",
        "172.16.0.0/12,10.0.0.0/8,192.168.0.0/16,127.0.0.0/8,fd00::/8,::1/128",
    )
    cfg["http"]["listeners"] = [
        {
            "name": "web",
            "resources": [
                {"name": "discovery"},
                {"name": "human"},
                {"name": "oauth"},
                {"name": "compat"},
                {"name": "graphql", "playground": False},
                {"name": "assets", "path": "/usr/local/share/mas-cli/assets/"},
                {"name": "adminapi"},
                {"name": "health"},
            ],
            "binds": [{"host": "0.0.0.0", "port": 8080}],
            "proxy_protocol": False,
        }
    ]

    cfg["database"] = {
        "uri": db_uri,
        "min_connections": 1,
        "max_connections": 10,
    }
    cfg["matrix"] = {
        "kind": "synapse",
        "homeserver": required("SYNAPSE_SERVER_NAME"),
        "endpoint": "http://synapse:8008",
        "secret": required("MAS_SHARED_SECRET"),
    }

    cfg.setdefault("passwords", {})["enabled"] = True
    cfg["passwords"]["minimum_complexity"] = 3

    account = cfg.setdefault("account", {})
    account["password_registration_enabled"] = True
    account["password_registration_email_required"] = as_bool("MAS_EMAIL_REQUIRED", False)
    account["password_registration_token_required"] = as_bool(
        "MAS_REGISTRATION_TOKEN_REQUIRED", True
    )
    account["password_change_allowed"] = True
    account["password_recovery_enabled"] = False
    account["login_with_email_allowed"] = False
    account["email_change_allowed"] = True
    account["displayname_change_allowed"] = True
    account["account_deactivation_allowed"] = True

    cfg.setdefault("captcha", {})["service"] = None
    cfg.setdefault("email", {})["transport"] = "blackhole"
    cfg.setdefault("branding", {})["service_name"] = required("MAS_BRAND_NAME")

    write_yaml(config_path, cfg)

    config_dir.chmod(0o700)
    config_path.chmod(0o600)
    os.chown(config_dir, 65532, 65532)
    os.chown(config_path, 65532, 65532)

    print("[config-init] MAS configuration ready")


def generate_element() -> None:
    base_url = required("SYNAPSE_PUBLIC_BASEURL").rstrip("/")
    server_name = required("SYNAPSE_SERVER_NAME")
    element_url = required("ELEMENT_WEB_URL").rstrip("/")

    config = {
        "default_server_name": server_name,
        "default_server_config": {
            "m.homeserver": {
                "base_url": base_url,
                "server_name": server_name,
            }
        },
        "permalink_prefix": element_url,
        "disable_custom_urls": True,
        "disable_guests": True,
        "brand": optional("ELEMENT_BRAND", "Element"),
        "default_theme": optional("ELEMENT_DEFAULT_THEME", "dark"),
        "room_directory": {"servers": [server_name]},
        "show_labs_settings": False,
    }
    write_json(Path("/generated/element/config.json"), config)
    print("[config-init] Element Web configuration ready")


def generate_livekit() -> None:
    config = {
        "port": 7880,
        "log_level": optional("LIVEKIT_LOG_LEVEL", "info"),
        "rtc": {
            "node_ip": required("PUBLIC_IP"),
            "use_external_ip": False,
            "tcp_port": 7881,
            "port_range_start": int(required("LIVEKIT_UDP_PORT_START")),
            "port_range_end": int(required("LIVEKIT_UDP_PORT_END")),
        },
        "room": {"auto_create": False},
        "keys": {required("LIVEKIT_KEY"): required("LIVEKIT_SECRET")},
        "webhook": {
            "api_key": required("LIVEKIT_KEY"),
            "urls": ["http://lk-jwt-service:8080/sfu_webhook"],
        },
    }
    write_yaml(Path("/generated/livekit/livekit.yaml"), config)
    print("[config-init] LiveKit configuration ready")


def main() -> int:
    try:
        generate_synapse()
        generate_mas()
        generate_element()
        generate_livekit()
    except Exception as exc:  # noqa: BLE001 - fail with a concise init error
        print(f"[config-init] ERROR: {exc}", file=sys.stderr)
        return 1

    print("[config-init] All configuration files are ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
