# Portainer deployment

[Русская версия](ru/portainer.md)

Create a Git-based Stack pointing to the repository `main` branch and `compose.yaml`. Load the generated `.env` as Stack environment variables.

Required custom images:

```text
ghcr.io/<GHCR_OWNER>/matrix-federated-gcp-config:main
ghcr.io/<GHCR_OWNER>/matrix-federated-gcp-haproxy:main
```

Before deployment confirm `PUBLIC_IP`, `PUBLIC_DOMAIN`, Cloudflare variables and GHCR owner. Enable pull/re-pull when deploying a newly published `main` image.

Element Admin is optional. Set `COMPOSE_PROFILES=admin` and create the `panel` DNS record only if it is required.
