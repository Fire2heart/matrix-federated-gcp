# Matrix Federated GCP

Публичный self-hosted Matrix deployment для виртуальной машины Google Cloud Compute Engine.

Стек включает Synapse, Matrix Authentication Service (MAS), Element Web, MatrixRTC/LiveKit, один PostgreSQL с отдельными базами Synapse и MAS, Redis, HAProxy и автоматический TLS Let's Encrypt через Cloudflare DNS-01.

Federation включена по умолчанию. Другие Matrix homeserver подключаются к серверу по HTTPS на порту 443.

[English version](README.md)

## Схема deployment

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

## Требования

- Google Cloud project с Compute Engine.
- VM Ubuntu 24.04 LTS.
- Зарезервированный статический внешний IPv4.
- Домен в Cloudflare DNS.
- Cloudflare API Token с `Zone / DNS / Edit` для нужной зоны.
- Docker Engine и Docker Compose plugin.
- Git repository с проектом.

Подробнее: [docs/ru/requirements.md](docs/ru/requirements.md).

## 1. Создать GCP VM

Практическая стартовая конфигурация:

- Ubuntu 24.04 LTS;
- 2 vCPU;
- минимум 4 GB RAM, 8 GB рекомендуется при более активном использовании;
- 50 GB persistent disk;
- зарезервированный static external IPv4.

Откройте TCP 80/443/7881 и UDP 50000-50050. TCP 22 ограничьте доверенными источниками администратора.

Подробнее: [docs/ru/gcp.md](docs/ru/gcp.md).

## 2. Клонировать repository

После установки Git и Docker Engine:

```bash
git clone <repository-url>
cd matrix-federated-gcp
```

Собственные images `config-init` и HAProxy собираются локально из checkout репозитория. Собственные GHCR/Docker Hub packages не нужны. Подробнее: [docs/ru/local-builds.md](docs/ru/local-builds.md).

GitHub Actions используются только для validation/CI и не публикуют deployment images.

## 3. Создать `.env`

```bash
python3 scripts/setup-env.py --lang ru
```

Мастер запрашивает публичный домен, статический IP VM, Cloudflare Zone ID/API Token, ACME email и первоначального MAS-администратора. Пароли PostgreSQL, MAS, Redis и LiveKit генерируются автоматически.

Проверка:

```bash
python3 scripts/check-env.py .env
```

## 4. Создать DNS

Для `example.com` создайте DNS-only A records на static IP VM:

```text
matrix.example.com   A  <STATIC_IP>
mas.example.com      A  <STATIC_IP>
element.example.com  A  <STATIC_IP>
rtc.example.com      A  <STATIC_IP>
rtc-jwt.example.com  A  <STATIC_IP>
```

`panel.example.com` нужен только при включённом Element Admin.

## 5. Deploy

```bash
docker compose --env-file .env pull
docker compose --env-file .env build --pull config-init haproxy
docker compose --env-file .env up -d
docker compose --env-file .env ps
```

При первой инициализации PostgreSQL `postgres/init-databases.sh` создаёт две изолированные базы и роли: `synapse` и `mas`.

## 6. Проверка

```bash
python3 scripts/smoke-test.sh .env
```

Federation:

```bash
curl -fsS https://matrix.example.com/.well-known/matrix/server
curl -fsS https://matrix.example.com/_matrix/federation/v1/version
```

## Документация

- [Требования](docs/ru/requirements.md)
- [GCP](docs/ru/gcp.md)
- [Локальная сборка images](docs/ru/local-builds.md)
- [Environment](docs/ru/env.md)
- [DNS](docs/ru/dns.md)
- [Federation](docs/ru/federation.md)
- [Архитектура](docs/ru/architecture.md)
- [Portainer](docs/ru/portainer.md)
- [Validation](docs/ru/validation.md)
- [Operations](docs/ru/operations.md)
- [Backup/restore](docs/ru/backup-restore.md)
- [Troubleshooting](docs/ru/troubleshooting.md)
