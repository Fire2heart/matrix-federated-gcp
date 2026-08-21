# GHCR

[Русская версия](ru/ghcr.md)

GitHub Actions publishes two images:

```text
ghcr.io/<owner>/matrix-federated-gcp-config:main
ghcr.io/<owner>/matrix-federated-gcp-haproxy:main
```

`GHCR_OWNER` in `.env` must match the package owner. Public packages can be pulled without registry credentials. Private packages require GHCR credentials on the Docker host or in Portainer.

The workflows derive the package namespace from `github.repository_owner`, so forks publish under the fork owner's namespace.
