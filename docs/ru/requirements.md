# Требования

[English](../requirements.md)

## Google Cloud

- Включён Compute Engine.
- VM Ubuntu 24.04 LTS.
- Рекомендуемый минимум: 2 vCPU, 8 GB RAM, 50 GB disk.
- Зарезервированный статический внешний IPv4.
- Firewall: TCP 80, 443, 7881; UDP 50000-50050.
- SSH по возможности ограничен доверенными административными source IP.

## DNS и TLS

- Домен управляется через Cloudflare DNS.
- API Token для выбранной зоны с `Zone / DNS / Edit`.
- Zone ID.

## Репозиторий

- GitHub repository.
- Включён GitHub Actions.
- GHCR packages доступны VM.

## ПО на VM

- Git.
- Docker Engine.
- Docker Compose plugin.
- Python 3 для setup/validation scripts.
