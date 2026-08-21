# Validation

[English](../validation.md)

GitHub Actions `Validate repository` — единственный обязательный CI workflow. Он проверяет инварианты репозитория, Python/shell syntax, генерацию `.env`, Compose rendering, обе локальные сборки, инициализацию общего PostgreSQL, сгенерированные конфиги Synapse/MAS и синтаксис HAProxy. Deployment images в registry не публикуются.

## Локальные проверки

Один раз создайте development environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Затем:

```bash
python scripts/validate-repo.py
python scripts/test-env-tools.py
```

Docker-specific integration checks выполняются в GitHub Actions.

## Runtime

```bash
docker compose --env-file .env ps
./scripts/smoke-test.sh .env
```

Smoke test намеренно небольшой: он проверяет публичные client/federation endpoints Synapse, Matrix well-known, MAS OIDC discovery, конфиг Element и health endpoint RTC JWT. Он не заменяет реальный тест login/message/federation/media.

## Federation

```bash
curl -fsS https://matrix.example.com/.well-known/matrix/server
curl -fsS https://matrix.example.com/_matrix/federation/v1/version
```
