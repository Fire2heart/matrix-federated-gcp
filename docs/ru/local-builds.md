# Локальная сборка custom images

[English](../local-builds.md)

В репозитории есть два небольших build context: `config-image/` и `haproxy/`. Docker Compose собирает их локально на deployment-host. Собственный container registry проекту не нужен.

```bash
docker compose --env-file .env build config-init haproxy
docker compose --env-file .env up -d
```

При обычном обновлении выполните `git pull`, обновите upstream images через `docker compose --env-file .env pull --ignore-buildable`, пересоберите `config-init` и `haproxy`, затем выполните `docker compose --env-file .env up -d`. Официальные upstream images (Synapse, MAS, Element, LiveKit, PostgreSQL, Redis и acme.sh) по-прежнему скачиваются из их официальных registries.

Base images для локальной сборки задаются в `.env` (`SYNAPSE_IMAGE`, `MAS_IMAGE`, `HAPROXY_BASE_IMAGE`). В Dockerfile намеренно нет запасных версий: единственный источник версий — `.env`.
