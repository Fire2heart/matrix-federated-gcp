# Environment configuration

[English](../env.md)

Создавайте `.env` через `python3 scripts/setup-env.py --lang ru`. Файл содержит секреты и не должен попадать в Git.

Основные значения:

- `PUBLIC_DOMAIN`, `PUBLIC_IP`;
- `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ZONE_ID`;
- `POSTGRES_ADMIN_PASSWORD` для общего PostgreSQL instance;
- `SYNAPSE_DB_USER/NAME/PASSWORD`;
- `MAS_DB_USER/NAME/PASSWORD`;
- секреты MAS, Redis и LiveKit.

Synapse и MAS используют разные credentials и разные databases, хотя работают через один PostgreSQL container.

Проверка без вывода секретов:

```bash
python3 scripts/check-env.py .env
```
