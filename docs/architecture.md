# Architecture

[Русская версия](ru/architecture.md)

- HAProxy is the only HTTP/HTTPS ingress and publishes TCP 80/443.
- Synapse serves Matrix client API and federation through HAProxy.
- MAS provides authentication.
- Element Web is the browser client.
- LiveKit and lk-jwt-service provide MatrixRTC.
- A single PostgreSQL 16 instance hosts two separate databases and roles: `synapse` and `mas`.
- Redis remains private and is used by lk-jwt-service.
- acme.sh obtains a wildcard certificate with Cloudflare DNS-01.
- LiveKit publishes TCP 7881 and the configured UDP media range directly on the GCP VM.
- `config-init` and HAProxy are built locally from repository Dockerfiles; project-owned registry packages are not required.

```text
Internet -> GCP firewall -> HAProxy -> Synapse / MAS / Element / RTC JWT
                              |
                              +-> Synapse federation/client API

Synapse ----> PostgreSQL <---- MAS
              |- synapse DB / synapse role
              `- mas DB     / mas role

Internet -> GCP firewall -> LiveKit media ports
```
