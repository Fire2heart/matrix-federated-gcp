# Backup and restore

[Русская версия](ru/backup-restore.md)

Back up the persistent Docker volumes and keep a protected copy of `.env`. For PostgreSQL, prefer database-aware backups (`pg_dump`) in addition to volume-level backups. Test restore procedures before relying on them for production.

Persistent state includes Synapse data/database, MAS configuration/database, Redis state and TLS/ACME state.
