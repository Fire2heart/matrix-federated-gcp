# GHCR

[English](../ghcr.md)

GitHub Actions публикует два image:

```text
ghcr.io/<owner>/matrix-federated-gcp-config:main
ghcr.io/<owner>/matrix-federated-gcp-haproxy:main
```

`GHCR_OWNER` в `.env` должен совпадать с владельцем packages. Public packages скачиваются без registry credentials. Для private packages нужна авторизация GHCR на Docker-host/в Portainer.

Workflow использует `github.repository_owner`, поэтому fork автоматически публикует packages в namespace владельца fork.
