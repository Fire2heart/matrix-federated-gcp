# Environment configuration

[English](../env.md)

Создавайте `.env` через `scripts/setup-env.py`. Файл `.env` не коммитится в Git.

## Параметры установки

- `GHCR_OWNER`: владелец GitHub/GHCR.
- `PUBLIC_DOMAIN`: базовый DNS domain.
- `PUBLIC_IP`: статический публичный IP VM; этот адрес также сообщает LiveKit.
- `CLOUDFLARE_ZONE_ID`: Cloudflare Zone ID.
- `CLOUDFLARE_API_TOKEN`: token с DNS Edit.
- `ACME_EMAIL`: email Let's Encrypt.

Hostnames сервисов вычисляются из `PUBLIC_DOMAIN`.

## Persistent credentials

Пароли PostgreSQL, MAS, Redis и LiveKit генерируются автоматически. После создания persistent volumes эти credentials должны сохраняться. Для существующей установки используйте safe-update режим мастера.

## Проверка

```bash
python3 scripts/check-env.py .env
```
