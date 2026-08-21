# Validation

[Русская версия](ru/validation.md)

GitHub Actions `Validate repository` checks Python/shell syntax, `.env` generation, Compose rendering, the PostgreSQL init script, both local custom image builds and HAProxy configuration. It does not publish deployment images.

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
