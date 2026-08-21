#!/usr/bin/env python3
"""EN: Interactive .env setup wizard.
RU: Интерактивный мастер настройки .env.
"""

from __future__ import annotations

import argparse
import getpass
import ipaddress
import shutil
from datetime import datetime

from env_tools import ROOT, parse_env, render_env, validate_env_content, write_secure_atomic


MESSAGES = {
    "en": {
        "title": "matrix-federated-gcp — environment setup",
        "intro": "Secrets are not printed. The resulting .env is written with file mode 600.",
        "required": "A value is required. Try again.",
        "bad_ip": "Invalid public IP address. Example: 34.120.10.20",
        "found": "Existing .env found.",
        "opt1": "1 — safe update: preserve persistent-service credentials (recommended)",
        "opt2": "2 — fresh environment: generate new credentials (new/reset installation only)",
        "opt3": "3 — exit",
        "choice": "Selection",
        "unchanged": "No changes were made.",
        "fresh_warning": "New credentials must not be used with persistent volumes that were initialized with different credentials.",
        "fresh_confirm": "Type NEW to confirm a new/reset installation: ",
        "cancelled": "Cancelled. No changes were made.",
        "unknown": "Unknown selection. No changes were made.",
        "domain": "Public domain",
        "owner": "GitHub/GHCR owner",
        "public_ip": "GCP VM static public IP (PUBLIC_IP)",
        "zone_id": "Cloudflare Zone ID",
        "email": "Email for Let's Encrypt/acme.sh",
        "admin_user": "Initial MAS administrator username",
        "admin_display": "Administrator display name",
        "admin_keep": "Initial MAS administrator bootstrap values are preserved for this installation.",
        "token_keep": "Cloudflare API Token (Enter = keep current): ",
        "token_new": "Cloudflare API Token (hidden input): ",
        "token_required": "A token is required for automatic TLS through DNS-01.",
        "validation_failed": "Validation failed. The existing .env was not modified:",
        "backup": "Environment backup created: {name}",
        "done": "Created: {path}",
        "mode_fresh": "Mode: NEW INSTALLATION — new persistent-service credentials were generated.",
        "mode_safe": "Mode: SAFE UPDATE — existing persistent-service credentials were preserved.",
        "valid": "[OK] Environment validation passed.",
        "next": "Next: load .env into the Portainer stack Environment variables.",
        "git": "Do not commit .env to Git.",
    },
    "ru": {
        "title": "matrix-federated-gcp — настройка окружения",
        "intro": "Секреты не выводятся на экран. Итоговый .env создаётся с правами 600.",
        "required": "Значение обязательно. Попробуйте ещё раз.",
        "bad_ip": "Некорректный публичный IP-адрес. Пример: 34.120.10.20",
        "found": "Найден существующий .env.",
        "opt1": "1 — безопасное обновление: сохранить credentials persistent-сервисов (рекомендуется)",
        "opt2": "2 — новое окружение: сгенерировать новые credentials (только новая/сброшенная установка)",
        "opt3": "3 — выйти",
        "choice": "Выбор",
        "unchanged": "Изменения не внесены.",
        "fresh_warning": "Новые credentials нельзя использовать с persistent volumes, инициализированными с другими credentials.",
        "fresh_confirm": "Введите NEW для подтверждения новой/сброшенной установки: ",
        "cancelled": "Отменено. Изменения не внесены.",
        "unknown": "Неизвестный вариант. Изменения не внесены.",
        "domain": "Публичный домен",
        "owner": "GitHub/GHCR owner",
        "public_ip": "Статический публичный IP VM в GCP (PUBLIC_IP)",
        "zone_id": "Cloudflare Zone ID",
        "email": "Email для Let's Encrypt/acme.sh",
        "admin_user": "Username первоначального MAS-администратора",
        "admin_display": "Отображаемое имя администратора",
        "admin_keep": "Bootstrap-параметры первоначального MAS-администратора сохраняются для этой установки.",
        "token_keep": "Cloudflare API Token (Enter = сохранить текущий): ",
        "token_new": "Cloudflare API Token (ввод скрыт): ",
        "token_required": "Token обязателен для автоматического TLS через DNS-01.",
        "validation_failed": "Проверка не пройдена. Существующий .env не изменён:",
        "backup": "Создан backup окружения: {name}",
        "done": "Создан: {path}",
        "mode_fresh": "Режим: НОВАЯ УСТАНОВКА — созданы новые credentials persistent-сервисов.",
        "mode_safe": "Режим: БЕЗОПАСНОЕ ОБНОВЛЕНИЕ — существующие credentials сохранены.",
        "valid": "[OK] Environment validation passed.",
        "next": "Следующий шаг: загрузить .env в Environment variables стека Portainer.",
        "git": "Не коммитьте .env в Git.",
    },
}


def ask(label: str, msg: dict[str, str], default: str = "", *, required: bool = True) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"{label}{suffix}: ").strip()
        if value:
            return value
        if default:
            return default
        if not required:
            return ""
        print(f"  {msg['required']}")


def ask_ip(label: str, msg: dict[str, str], default: str = "") -> str:
    while True:
        value = ask(label, msg, default)
        try:
            ipaddress.ip_address(value)
            return value
        except ValueError:
            print(f"  {msg['bad_ip']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or update the matrix-federated-gcp .env file.")
    parser.add_argument("--lang", choices=("en", "ru"), default="en", help="Wizard language (default: en)")
    args = parser.parse_args()
    msg = MESSAGES[args.lang]

    target = ROOT / ".env"
    existing, _ = parse_env(target)

    print(f"\n{msg['title']}")
    print("=" * len(msg["title"]))
    print(f"{msg['intro']}\n")

    fresh = not target.exists()
    if target.exists():
        print(msg["found"])
        print(f"  {msg['opt1']}")
        print(f"  {msg['opt2']}")
        print(f"  {msg['opt3']}")
        choice = ask(msg["choice"], msg, "1")
        if choice == "3":
            print(msg["unchanged"])
            return 0
        if choice == "2":
            print(f"\n{msg['fresh_warning']}")
            confirmation = input(msg["fresh_confirm"]).strip()
            if confirmation != "NEW":
                print(msg["cancelled"])
                return 2
            fresh = True
        elif choice != "1":
            print(msg["unknown"])
            return 2
        else:
            fresh = False

    domain = ask(msg["domain"], msg, existing.get("PUBLIC_DOMAIN", ""))
    ghcr_owner = ask(msg["owner"], msg, existing.get("GHCR_OWNER", ""))
    public_ip = ask_ip(msg["public_ip"], msg, existing.get("PUBLIC_IP", ""))
    zone_id = ask(msg["zone_id"], msg, existing.get("CLOUDFLARE_ZONE_ID", ""))
    acme_email = ask(msg["email"], msg, existing.get("ACME_EMAIL", ""), required=False)

    if fresh:
        admin_user = ask(msg["admin_user"], msg, "admin")
        admin_display = ask(msg["admin_display"], msg, "Administrator")
    else:
        admin_user = existing.get("MAS_ADMIN_USER", "admin")
        admin_display = existing.get("MAS_ADMIN_DISPLAY_NAME", "Administrator")
        print(msg["admin_keep"])

    current_token = existing.get("CLOUDFLARE_API_TOKEN", "") if not fresh else ""
    while True:
        if current_token and not current_token.startswith("CHANGE_ME"):
            token = getpass.getpass(msg["token_keep"]).strip() or current_token
        else:
            token = getpass.getpass(msg["token_new"]).strip()
        if token:
            break
        print(f"  {msg['token_required']}")

    content = render_env(
        domain=domain,
        ghcr_owner=ghcr_owner,
        public_ip=public_ip,
        cloudflare_zone_id=zone_id,
        cloudflare_api_token=token,
        acme_email=acme_email,
        admin_user=admin_user,
        admin_display_name=admin_display,
        existing=existing,
        fresh=fresh,
    )

    errors = validate_env_content(content)
    if errors:
        print(f"\n{msg['validation_failed']}")
        for error in errors:
            print(f"  [ERROR] {error}")
        return 1

    if target.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = ROOT / f".env.backup-{stamp}"
        shutil.copy2(target, backup)
        backup.chmod(0o600)
        print(msg["backup"].format(name=backup.name))

    write_secure_atomic(target, content)
    print(f"\n{msg['done'].format(path=target)}")
    print(msg["mode_fresh"] if fresh else msg["mode_safe"])
    print(f"\n{msg['valid']}")
    print(msg["next"])
    print(msg["git"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
