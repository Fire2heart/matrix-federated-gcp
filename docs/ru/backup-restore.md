# Backup и restore

[English](../backup-restore.md)

Храните защищённую копию `.env` и backup persistent Docker volumes. Для PostgreSQL дополнительно делайте отдельные logical dumps:

```bash
docker compose --env-file .env exec -T postgres pg_dump -U synapse synapse > synapse.sql
docker compose --env-file .env exec -T postgres pg_dump -U mas mas > mas.sql
```

Один PostgreSQL volume содержит обе logical databases, но они остаются раздельными и должны backup/restore отдельно. Также сохраняйте Synapse state, MAS config, Redis и TLS/ACME state.
