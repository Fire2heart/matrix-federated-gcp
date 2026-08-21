# Backup and restore

[Русская версия](ru/backup-restore.md)

Keep a protected copy of `.env` and back up persistent Docker volumes. For PostgreSQL, use database-aware backups in addition to volume-level backups:

```bash
docker compose --env-file .env exec -T postgres pg_dump -U synapse synapse > synapse.sql
docker compose --env-file .env exec -T postgres pg_dump -U mas mas > mas.sql
```

The single PostgreSQL volume contains both logical databases, but they remain separate and should be dumped/restored independently. Persistent state also includes Synapse media/config, MAS config, Redis and TLS/ACME state.
