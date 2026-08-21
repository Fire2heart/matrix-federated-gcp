# Local custom image builds

[Русская версия](ru/local-builds.md)

This repository has two small custom build contexts: `config-image/` and `haproxy/`. They are built locally on the deployment host by Docker Compose. No project-owned container registry is required.

```bash
docker compose --env-file .env build config-init haproxy
docker compose --env-file .env up -d
```

For a normal update, pull the Git repository, refresh upstream images with `docker compose --env-file .env pull --ignore-buildable`, rebuild `config-init` and `haproxy`, then run `docker compose --env-file .env up -d`. Official upstream images (Synapse, MAS, Element, LiveKit, PostgreSQL, Redis and acme.sh) are still pulled from their upstream registries.

The base images used by the local builds are configured in `.env` (`SYNAPSE_IMAGE`, `MAS_IMAGE`, `HAPROXY_BASE_IMAGE`). The Dockerfiles intentionally do not contain fallback versions, so `.env` is the single source of image versions.
