# Requirements

[Русская версия](ru/requirements.md)

## Google Cloud

- Compute Engine VM with Ubuntu 24.04 LTS.
- 2 vCPU.
- 4 GB RAM minimum; 8 GB is preferable for heavier use.
- Persistent disk sized for media/database growth.
- Reserved static public IP.
- Firewall: TCP 80/443/7881 and configured LiveKit UDP range.

## DNS / TLS

- Domain hosted in Cloudflare.
- DNS-only records for Matrix endpoints.
- Cloudflare API Token with DNS edit permission for the selected zone.

## Host software

- Git.
- Docker Engine.
- Docker Compose plugin with local build support.
- Outbound Internet access for official upstream container registries, Let's Encrypt and Cloudflare API.

No project-owned GHCR or Docker Hub images are required.
