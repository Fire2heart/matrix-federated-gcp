# Troubleshooting

[English](../troubleshooting.md)

## HAProxy 503

```bash
docker compose --env-file .env ps
docker compose --env-file .env logs --tail=200 haproxy
```

## Synapse unhealthy

```bash
docker compose --env-file .env logs --tail=200 synapse
docker compose --env-file .env logs --tail=200 synapse-db
```

## ACME/TLS

```bash
docker compose --env-file .env logs --tail=200 acme
```

Проверьте Cloudflare token permissions и Zone ID.

## Federation не работает

Проверьте public DNS, GCP firewall TCP 443 и:

```bash
curl -v https://matrix.example.com/.well-known/matrix/server
curl -v https://matrix.example.com/_matrix/federation/v1/version
```

## Звонок устанавливается, но нет media

Проверьте `PUBLIC_IP`, GCP firewall TCP 7881 и UDP 50000-50050, затем LiveKit logs.
