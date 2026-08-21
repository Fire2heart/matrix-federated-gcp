# Troubleshooting

[English](../troubleshooting.md)

## Статус

```bash
docker compose --env-file .env ps -a
```

## PostgreSQL

```bash
docker compose --env-file .env logs --tail=200 postgres
docker compose --env-file .env exec postgres psql -U postgres -d postgres -c '\l'
```

После fresh initialization должны существовать отдельные databases `synapse` и `mas`.

## Application logs

```bash
docker compose --env-file .env logs --tail=200 synapse mas haproxy
```

## Пересборка локальных custom images

```bash
docker compose --env-file .env build --no-cache config-init haproxy
docker compose --env-file .env up -d
```
