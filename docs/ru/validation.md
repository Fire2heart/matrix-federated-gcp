# Validation

[English](../validation.md)

GitHub Actions `Validate repository` проверяет Python/shell syntax, генерацию `.env`, Compose rendering, PostgreSQL init script, сборку двух локальных custom images и HAProxy config. Deployment images в registry не публикуются.

Runtime:

```bash
docker compose --env-file .env ps
python3 scripts/smoke-test.sh .env
```

Federation:

```bash
curl -fsS https://matrix.example.com/.well-known/matrix/server
curl -fsS https://matrix.example.com/_matrix/federation/v1/version
```
