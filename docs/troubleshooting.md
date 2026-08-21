# Troubleshooting

[Русская версия](ru/troubleshooting.md)

## 503 from HAProxy

Check container state and HAProxy backend connectivity:

```bash
docker compose --env-file .env ps
docker compose --env-file .env logs --tail=200 haproxy
```

## Synapse unhealthy

```bash
docker compose --env-file .env logs --tail=200 synapse
docker compose --env-file .env logs --tail=200 synapse-db
```

## ACME/TLS failure

```bash
docker compose --env-file .env logs --tail=200 acme
```

Check Cloudflare token permissions and Zone ID.

## Federation unavailable

Confirm public DNS, GCP TCP 443 firewall and:

```bash
curl -v https://matrix.example.com/.well-known/matrix/server
curl -v https://matrix.example.com/_matrix/federation/v1/version
```

## Calls connect but media fails

Check `PUBLIC_IP`, GCP TCP 7881 and UDP 50000-50050 firewall rules, and the LiveKit logs.
