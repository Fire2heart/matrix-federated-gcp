# Operations

[Русская версия](ru/operations.md)

Normal update procedure:

```bash
git pull
python3 scripts/setup-env.py
python3 scripts/check-env.py .env
docker compose --env-file .env pull --ignore-buildable
docker compose --env-file .env build --pull config-init haproxy
docker compose --env-file .env up -d
./scripts/smoke-test.sh .env
```

Do not remove persistent volumes during a normal update. Do not rotate PostgreSQL/MAS/Redis/LiveKit credentials unless persistent state is intentionally reset.
