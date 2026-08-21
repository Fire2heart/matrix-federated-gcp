# Troubleshooting

[Русская версия](ru/troubleshooting.md)

## Status

```bash
docker compose --env-file .env ps -a
```

## PostgreSQL

```bash
docker compose --env-file .env logs --tail=200 postgres
docker compose --env-file .env exec postgres psql -U postgres -d postgres -c '\l'
```

A fresh initialization should show separate `synapse` and `mas` databases.

## Application logs

```bash
docker compose --env-file .env logs --tail=200 synapse mas haproxy
```

## Rebuild local custom images

```bash
docker compose --env-file .env build --no-cache config-init haproxy
docker compose --env-file .env up -d
```
