# Environment configuration

[Русская версия](ru/env.md)

Generate `.env` with `python3 scripts/setup-env.py`. The file contains secrets and must not be committed.

Important values include:

- `PUBLIC_DOMAIN`, `PUBLIC_IP`;
- `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ZONE_ID`;
- `POSTGRES_ADMIN_PASSWORD` for the shared PostgreSQL instance;
- `SYNAPSE_DB_USER/NAME/PASSWORD`;
- `MAS_DB_USER/NAME/PASSWORD`;
- MAS, Redis and LiveKit secrets.

Synapse and MAS use separate database credentials even though both databases run inside one PostgreSQL container.

Validate without printing secret values:

```bash
python3 scripts/check-env.py .env
```
