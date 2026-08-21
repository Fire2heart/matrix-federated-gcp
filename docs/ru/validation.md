# Проверка

[English](../validation.md)

## CI

`Validate repository` проверяет структуру repository, генерацию `.env`, Compose, shell syntax, сборку двух custom Docker image и HAProxy config.

## Runtime

```bash
docker compose --env-file .env ps
python3 scripts/smoke-test.sh .env
```

Federation:

```bash
curl -fsS https://matrix.example.com/.well-known/matrix/server
curl -fsS https://matrix.example.com/_matrix/federation/v1/version
```
