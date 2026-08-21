# Требования

[English](../requirements.md)

## Google Cloud

- Compute Engine VM с Ubuntu 24.04 LTS.
- 2 vCPU.
- Минимум 4 GB RAM; для более активной нагрузки желательно 8 GB.
- Persistent disk с запасом под media и databases.
- Зарезервированный static public IP.
- Firewall: TCP 80/443/7881 и настроенный LiveKit UDP range.

## DNS / TLS

- Домен в Cloudflare.
- DNS-only records для Matrix endpoints.
- Cloudflare API Token с правом DNS edit для зоны.

## Host software

- Git.
- Docker Engine.
- Docker Compose plugin с поддержкой local build.
- Исходящий Internet для официальных container registries, Let's Encrypt и Cloudflare API.

Собственные GHCR или Docker Hub images проекту не нужны.
