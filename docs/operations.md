# Operations

[Русская версия](ru/operations.md)

Normal update procedure:

```bash
git pull
python3 scripts/setup-env.py
python3 scripts/check-env.py .env
docker compose --env-file .env pull
docker compose --env-file .env up -d
python3 scripts/smoke-test.sh .env
```

Do not remove persistent volumes during a normal update. Do not rotate generated database/MAS/Redis/LiveKit credentials unless the corresponding persistent state is intentionally reset.
