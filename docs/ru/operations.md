# Эксплуатация

[English](../operations.md)

Обычное обновление:

```bash
git pull
python3 scripts/setup-env.py --lang ru
python3 scripts/check-env.py .env
docker compose --env-file .env pull
docker compose --env-file .env up -d
python3 scripts/smoke-test.sh .env
```

При обычном update persistent volumes не удаляются. Не меняйте сгенерированные credentials PostgreSQL/MAS/Redis/LiveKit без намеренного reset соответствующего state.
