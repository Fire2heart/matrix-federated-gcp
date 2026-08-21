# Local custom image builds

[Русская версия](ru/local-builds.md)

This repository has two small custom build contexts: `config-image/` and `haproxy/`. They are built locally on the deployment host by Docker Compose. No project-owned container registry is required.

```bash
docker compose --env-file .env build config-init haproxy
docker compose --env-file .env up -d
```

For a normal update, pull the Git repository and run `docker compose --env-file .env up -d --build`. Official upstream images (Synapse, MAS, Element, LiveKit, PostgreSQL, Redis and acme.sh) are still pulled from their upstream registries.
