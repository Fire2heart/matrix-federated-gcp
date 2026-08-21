# Validation

[Русская версия](ru/validation.md)

GitHub Actions `Validate repository` is the only required CI workflow. It checks repository invariants, Python/shell syntax, `.env` generation, Compose rendering, both local image builds, shared PostgreSQL initialization, generated Synapse/MAS configuration and HAProxy syntax. It does not publish deployment images.

## Local checks

Create a development environment once:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Then run:

```bash
python scripts/validate-repo.py
python scripts/test-env-tools.py
```

Docker-specific integration checks run in GitHub Actions.

## Runtime

```bash
docker compose --env-file .env ps
./scripts/smoke-test.sh .env
```

The smoke test is intentionally small: it verifies the public Synapse client/federation endpoints, Matrix well-known responses, MAS OIDC discovery, Element configuration and the RTC JWT health endpoint. It does not replace a real login/message/federation/media test.

## Federation

```bash
curl -fsS https://matrix.example.com/.well-known/matrix/server
curl -fsS https://matrix.example.com/_matrix/federation/v1/version
```
