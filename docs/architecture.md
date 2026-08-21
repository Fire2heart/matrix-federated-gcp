# Architecture

[Русская версия](ru/architecture.md)

- HAProxy is the only HTTP/HTTPS ingress and publishes TCP 80/443.
- Synapse serves both Matrix client API and federation through HAProxy.
- MAS provides authentication.
- Element Web is the browser client.
- LiveKit and lk-jwt-service provide MatrixRTC.
- PostgreSQL and Redis remain on private Docker networks.
- acme.sh obtains a wildcard certificate with Cloudflare DNS-01.
- LiveKit publishes TCP 7881 and the configured UDP media range directly on the GCP VM.

```text
Internet -> GCP firewall -> HAProxy -> application containers
                              |
                              +-> Synapse federation/client API
Internet -> GCP firewall -> LiveKit media ports
```
