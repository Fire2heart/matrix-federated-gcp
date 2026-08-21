# Environment configuration

[Русская версия](ru/env.md)

Generate `.env` with `scripts/setup-env.py`. Do not commit `.env`.

## Installation-specific values

- `GHCR_OWNER`: GitHub/GHCR owner.
- `PUBLIC_DOMAIN`: base DNS domain.
- `PUBLIC_IP`: GCP VM static public address; also advertised by LiveKit.
- `CLOUDFLARE_ZONE_ID`: Cloudflare Zone ID.
- `CLOUDFLARE_API_TOKEN`: DNS edit token.
- `ACME_EMAIL`: Let's Encrypt account email.

The wizard derives Matrix service hostnames from `PUBLIC_DOMAIN`.

## Persistent credentials

Database, MAS, Redis and LiveKit credentials are generated automatically. Once persistent Docker volumes exist, keep these credentials unchanged. Use the wizard safe-update mode for an existing installation.

## Validate

```bash
python3 scripts/check-env.py .env
```
