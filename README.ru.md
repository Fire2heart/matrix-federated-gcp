# Matrix Federated GCP

Публичный self-hosted Matrix для Google Cloud Compute Engine.

Стек включает Synapse, Matrix Authentication Service (MAS), Element Web, MatrixRTC/LiveKit, PostgreSQL, Redis, HAProxy и автоматический TLS через Let's Encrypt + Cloudflare DNS-01.

Федерация включена по умолчанию. Другие Matrix homeserver могут обращаться к серверу по HTTPS на порту 443.

[English version](README.md)

## Схема

```text
Internet
   |
   v
Cloudflare DNS
   |
   v
Статический публичный IP GCP
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

## Требования

- Google Cloud project с Compute Engine.
- VM Ubuntu 24.04 LTS.
- Зарезервированный статический внешний IPv4.
- Домен в Cloudflare DNS.
- Cloudflare API Token с `Zone / DNS / Edit` для нужной зоны.
- Docker Engine и Docker Compose plugin.
- GitHub repository и GitHub Actions.
- GHCR packages для custom config и HAProxy images.

Подробнее: [docs/ru/requirements.md](docs/ru/requirements.md).

## 1. Создать VM в GCP

Рекомендуемый стартовый размер:

- Ubuntu 24.04 LTS
- 2 vCPU
- 8 GB RAM
- 50 GB balanced persistent disk
- статический внешний IPv4

Firewall:

- TCP 80
- TCP 443
- TCP 7881
- UDP 50000-50050
- TCP 22 только с доверенных административных адресов

Подробно: [docs/ru/gcp.md](docs/ru/gcp.md).

## 2. Создать или форкнуть репозиторий

Репозиторий публикует два custom image:

```text
ghcr.io/<owner>/matrix-federated-gcp-config:main
ghcr.io/<owner>/matrix-federated-gcp-haproxy:main
```

После push должны успешно завершиться:

```text
Validate repository
Publish config image
Publish HAProxy image
```

Подробнее: [docs/ru/ghcr.md](docs/ru/ghcr.md).

## 3. Установить Docker и клонировать репозиторий

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
```

После установки Docker Engine:

```bash
git clone https://github.com/<owner>/<repository>.git
cd <repository>
```

## 4. Создать `.env`

Русский мастер:

```bash
python3 scripts/setup-env.py --lang ru
```

English:

```bash
python3 scripts/setup-env.py
```

Мастер запрашивает:

- публичный домен;
- GitHub/GHCR owner;
- статический публичный IP VM;
- Cloudflare Zone ID;
- Cloudflare API Token;
- email для ACME;
- первоначального MAS-администратора.

Сервисные пароли генерируются автоматически.

Проверка:

```bash
python3 scripts/check-env.py .env
```

Подробнее: [docs/ru/env.md](docs/ru/env.md).

## 5. Создать DNS

Для `example.com`:

```text
matrix.example.com   A  <STATIC_IP>
mas.example.com      A  <STATIC_IP>
element.example.com  A  <STATIC_IP>
rtc.example.com      A  <STATIC_IP>
rtc-jwt.example.com  A  <STATIC_IP>
```

Все записи — DNS only. `panel.example.com` создаётся только при необходимости Element Admin.

Подробнее: [docs/ru/dns.md](docs/ru/dns.md).

## 6. Deploy

Через Docker Compose:

```bash
docker compose --env-file .env pull
docker compose --env-file .env up -d
```

Через Portainer: [docs/ru/portainer.md](docs/ru/portainer.md).

## 7. Проверить

```bash
python3 scripts/smoke-test.sh .env
```

Федерация:

```bash
curl -fsS https://matrix.example.com/.well-known/matrix/server
curl -fsS https://matrix.example.com/_matrix/federation/v1/version
```

Подробнее: [docs/ru/federation.md](docs/ru/federation.md).

## Документация

- [Требования](docs/ru/requirements.md)
- [GCP](docs/ru/gcp.md)
- [GHCR](docs/ru/ghcr.md)
- [Environment](docs/ru/env.md)
- [DNS](docs/ru/dns.md)
- [Федерация](docs/ru/federation.md)
- [Архитектура](docs/ru/architecture.md)
- [Portainer](docs/ru/portainer.md)
- [Проверка](docs/ru/validation.md)
- [Эксплуатация](docs/ru/operations.md)
- [Backup/restore](docs/ru/backup-restore.md)
- [Troubleshooting](docs/ru/troubleshooting.md)
