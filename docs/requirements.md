# Requirements

[Русская версия](ru/requirements.md)

## Google Cloud

- Compute Engine enabled.
- Ubuntu 24.04 LTS VM.
- Recommended minimum: 2 vCPU, 8 GB RAM, 50 GB disk.
- Reserved static external IPv4.
- Firewall access: TCP 80, 443, 7881; UDP 50000-50050.
- SSH restricted to trusted administrator source addresses where possible.

## DNS and TLS

- Domain managed in Cloudflare DNS.
- API Token scoped to the selected zone with `Zone / DNS / Edit`.
- Zone ID.

## Repository

- GitHub repository.
- GitHub Actions enabled.
- GHCR packages available to the VM.

## VM software

- Git.
- Docker Engine.
- Docker Compose plugin.
- Python 3 for setup/validation scripts.
