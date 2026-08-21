# Архитектура

[English](../architecture.md)

- HAProxy — единственный HTTP/HTTPS ingress и публикует TCP 80/443.
- Synapse обслуживает client API и federation через HAProxy.
- MAS отвечает за аутентификацию.
- Element Web — web-клиент.
- LiveKit и lk-jwt-service обеспечивают MatrixRTC.
- Один PostgreSQL 16 содержит две отдельные базы и роли: `synapse` и `mas`.
- Redis остаётся внутренним и используется lk-jwt-service.
- acme.sh получает wildcard certificate через Cloudflare DNS-01.
- LiveKit напрямую публикует TCP 7881 и настроенный UDP media range.
- `config-init` и HAProxy собираются локально из Dockerfile репозитория; собственный registry не нужен.

```text
Internet -> GCP firewall -> HAProxy -> Synapse / MAS / Element / RTC JWT

Synapse ----> PostgreSQL <---- MAS
              |- synapse DB / synapse role
              `- mas DB     / mas role

Internet -> GCP firewall -> LiveKit media ports
```
