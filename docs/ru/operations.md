# Operations

[English](../operations.md)

Обычное обновление:

```bash
git pull
python3 scripts/setup-env.py --lang ru
python3 scripts/check-env.py .env
docker compose --env-file .env pull --ignore-buildable
docker compose --env-file .env build --pull config-init haproxy
docker compose --env-file .env up -d
./scripts/smoke-test.sh .env
```

При обычном обновлении persistent volumes не удаляются. Не меняйте PostgreSQL/MAS/Redis/LiveKit credentials без намеренного сброса persistent state.
