# Локальная сборка custom images

[English](../local-builds.md)

В репозитории есть два небольших build context: `config-image/` и `haproxy/`. Docker Compose собирает их локально на deployment-host. Собственный container registry проекту не нужен.

```bash
docker compose --env-file .env build config-init haproxy
docker compose --env-file .env up -d
```

При обычном обновлении выполните `git pull`, затем `docker compose --env-file .env up -d --build`. Официальные upstream images (Synapse, MAS, Element, LiveKit, PostgreSQL, Redis и acme.sh) по-прежнему скачиваются из их официальных registries.
