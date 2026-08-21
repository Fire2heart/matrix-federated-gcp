# Backup и restore

[English](../backup-restore.md)

Сохраняйте persistent Docker volumes и защищённую копию `.env`. Для PostgreSQL желательно дополнительно использовать `pg_dump`, а не полагаться только на копию volume. Процедуру restore следует заранее протестировать.

Persistent state включает Synapse data/database, MAS config/database, Redis state и TLS/ACME state.
