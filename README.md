# Matrix Federated GCP

Self-hosted public Matrix deployment for a Google Cloud Compute Engine VM.

The stack provides Synapse, Matrix Authentication Service (MAS), Element Web, MatrixRTC/LiveKit, one PostgreSQL instance with separate Synapse and MAS databases, Redis, HAProxy and automatic TLS with Let's Encrypt through Cloudflare DNS-01.

Federation is enabled by default. Other Matrix homeservers reach the server over HTTPS on port 443.

[Русская версия](README.ru.md)

## Deployment model

```text
Internet
   |
   v
Cloudflare DNS
   |
   v
GCP static public IP
   |
   v
GCP firewall
   |
   v
HAProxy :80/:443
   |
   +-- matrix.example.com  -> Synapse
   +-- mas.example.com     -> MAS
   +-- element.example.com -> Element Web
   +-- rtc.example.com     -> LiveKit signalling
   +-- rtc-jwt.example.com -> MatrixRTC auth service

Synapse ----> PostgreSQL <---- MAS
              |- DB synapse / role synapse
              `- DB mas     / role mas

LiveKit media:
  TCP 7881
  UDP 50000-50050
```

## Requirements

- Google Cloud project with Compute Engine enabled.
- Ubuntu 24.04 LTS VM.
- Reserved static external IPv4 address.
- Domain hosted in Cloudflare DNS.
- Cloudflare API Token with `Zone / DNS / Edit` for the selected zone.
- Docker Engine and Docker Compose plugin.
- Git repository containing this project.

See [docs/requirements.md](docs/requirements.md).

## 1. Create the GCP VM

Practical starting configuration:

- Ubuntu 24.04 LTS;
- 2 vCPU;
- 4 GB RAM minimum, 8 GB recommended for more active use;
- 50 GB persistent disk;
- reserved static external IPv4.

Create firewall rules for TCP 80/443/7881, UDP 50000-50050, and restrict TCP 22 to trusted administrator sources.

Detailed instructions: [docs/gcp.md](docs/gcp.md).

## 2. Clone the repository

Install Git and Docker Engine, then clone the repository on the VM:

```bash
git clone <repository-url>
cd matrix-federated-gcp
```

The project-owned `config-init` and HAProxy images are built locally from this checkout. No project-owned GHCR/Docker Hub packages are required. See [docs/local-builds.md](docs/local-builds.md).

GitHub Actions are used only for validation/CI and do not publish deployment images.

## 3. Generate `.env`

English wizard:

```bash
python3 scripts/setup-env.py
```

Russian wizard:

```bash
python3 scripts/setup-env.py --lang ru
```

The wizard asks for the public domain, GCP VM static IP, Cloudflare Zone ID/API Token, ACME email and initial MAS administrator. It generates PostgreSQL, MAS, Redis and LiveKit credentials automatically.

Validate the result:

```bash
python3 scripts/check-env.py .env
```

See [docs/env.md](docs/env.md).

## 4. Create DNS records

For `example.com`, create DNS-only A records pointing to the VM static IP:

```text
matrix.example.com   A  <STATIC_IP>
mas.example.com      A  <STATIC_IP>
element.example.com  A  <STATIC_IP>
rtc.example.com      A  <STATIC_IP>
rtc-jwt.example.com  A  <STATIC_IP>
```

`panel.example.com` is optional and is only needed when Element Admin is enabled.

See [docs/dns.md](docs/dns.md).

## 5. Deploy

```bash
docker compose --env-file .env pull
docker compose --env-file .env build --pull config-init haproxy
docker compose --env-file .env up -d
docker compose --env-file .env ps
```

On the first PostgreSQL initialization, `postgres/init-databases.sh` creates two isolated databases and roles: `synapse` and `mas`.

## 6. Validate

```bash
python3 scripts/smoke-test.sh .env
```

Federation endpoints:

```bash
curl -fsS https://matrix.example.com/.well-known/matrix/server
curl -fsS https://matrix.example.com/_matrix/federation/v1/version
```

## Documentation

- [Requirements](docs/requirements.md)
- [GCP deployment](docs/gcp.md)
- [Local image builds](docs/local-builds.md)
- [Environment configuration](docs/env.md)
- [DNS](docs/dns.md)
- [Federation](docs/federation.md)
- [Architecture](docs/architecture.md)
- [Portainer](docs/portainer.md)
- [Validation](docs/validation.md)
- [Operations](docs/operations.md)
- [Backup and restore](docs/backup-restore.md)
- [Troubleshooting](docs/troubleshooting.md)
