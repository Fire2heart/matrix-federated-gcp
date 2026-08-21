# Validation

[Русская версия](ru/validation.md)

## CI

`Validate repository` verifies repository structure, `.env` generation, Compose parsing, shell syntax, both custom Docker builds and HAProxy configuration.

## Runtime

```bash
docker compose --env-file .env ps
python3 scripts/smoke-test.sh .env
```

Verify federation:

```bash
curl -fsS https://matrix.example.com/.well-known/matrix/server
curl -fsS https://matrix.example.com/_matrix/federation/v1/version
```
