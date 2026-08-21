# Matrix Federated GCP

Self-hosted public Matrix deployment for a Google Cloud Compute Engine VM.

The stack provides Synapse, Matrix Authentication Service (MAS), Element Web, MatrixRTC/LiveKit, PostgreSQL, Redis, HAProxy and automatic TLS with Let's Encrypt through Cloudflare DNS-01.

Federation is enabled by default. Other Matrix homeservers can reach this server over HTTPS on port 443.

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
- GitHub repository and GitHub Actions.
- GHCR packages for the custom config and HAProxy images.

See [docs/requirements.md](docs/requirements.md).

## 1. Create the GCP VM

Recommended starting configuration:

- Ubuntu 24.04 LTS
- 2 vCPU
- 8 GB RAM
- 50 GB balanced persistent disk
- reserved static external IPv4

Create firewall rules for:

- TCP 80
- TCP 443
- TCP 7881
- UDP 50000-50050
- TCP 22 only from trusted administrator source addresses

Detailed instructions: [docs/gcp.md](docs/gcp.md).

## 2. Create or fork the repository

The repository publishes two custom images:

```text
ghcr.io/<owner>/matrix-federated-gcp-config:main
ghcr.io/<owner>/matrix-federated-gcp-haproxy:main
```

After pushing the repository, wait for these GitHub Actions workflows to pass:

```text
Validate repository
Publish config image
Publish HAProxy image
```

See [docs/ghcr.md](docs/ghcr.md).

## 3. Install Docker and clone the repository

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
```

Install Docker Engine using Docker's official Ubuntu instructions, then clone the repository:

```bash
git clone https://github.com/<owner>/<repository>.git
cd <repository>
```

## 4. Generate `.env`

English wizard:

```bash
python3 scripts/setup-env.py
```

Russian wizard:

```bash
python3 scripts/setup-env.py --lang ru
```

The wizard asks for:

- public domain;
- GitHub/GHCR owner;
- GCP VM static public IP;
- Cloudflare Zone ID;
- Cloudflare API Token;
- ACME email;
- initial MAS administrator.

It generates service credentials automatically.

Validate the result:

```bash
python3 scripts/check-env.py .env
```

See [docs/env.md](docs/env.md).

## 5. Create DNS records

For `example.com`, create DNS-only records pointing to the VM static IP:

```text
matrix.example.com   A  <STATIC_IP>
mas.example.com      A  <STATIC_IP>
element.example.com  A  <STATIC_IP>
rtc.example.com      A  <STATIC_IP>
rtc-jwt.example.com  A  <STATIC_IP>
```

`panel.example.com` is optional and should only be created if Element Admin is enabled.

See [docs/dns.md](docs/dns.md).

## 6. Deploy

### Docker Compose

```bash
docker compose --env-file .env pull
docker compose --env-file .env up -d
```

### Portainer

Portainer can deploy the repository directly and load `.env` into Stack environment variables. See [docs/portainer.md](docs/portainer.md).

## 7. Validate the deployment

```bash
python3 scripts/smoke-test.sh .env
```

Check federation endpoints:

```bash
curl -fsS https://matrix.example.com/.well-known/matrix/server
curl -fsS https://matrix.example.com/_matrix/federation/v1/version
```

Expected server delegation uses HTTPS port 443. Details: [docs/federation.md](docs/federation.md).

## Documentation

- [Requirements](docs/requirements.md)
- [GCP deployment](docs/gcp.md)
- [GHCR](docs/ghcr.md)
- [Environment configuration](docs/env.md)
- [DNS](docs/dns.md)
- [Federation](docs/federation.md)
- [Architecture](docs/architecture.md)
- [Portainer](docs/portainer.md)
- [Validation](docs/validation.md)
- [Operations](docs/operations.md)
- [Backup and restore](docs/backup-restore.md)
- [Troubleshooting](docs/troubleshooting.md)
