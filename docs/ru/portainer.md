# Portainer deployment

[English](../portainer.md)

Создайте Git-based Stack на ветку `main` и `compose.yaml`. Загрузите сгенерированный `.env` как Stack environment variables.

Custom images:

```text
ghcr.io/<GHCR_OWNER>/matrix-federated-gcp-config:main
ghcr.io/<GHCR_OWNER>/matrix-federated-gcp-haproxy:main
```

Перед deploy проверьте `PUBLIC_IP`, `PUBLIC_DOMAIN`, Cloudflare variables и GHCR owner. При публикации нового `main` image включайте повторный pull.

Element Admin optional: установите `COMPOSE_PROFILES=admin` и создайте DNS `panel` только если он нужен.
