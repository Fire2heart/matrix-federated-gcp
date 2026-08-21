# Развёртывание в Google Cloud

[English](../gcp.md)

## VM

Создайте Compute Engine VM с Ubuntu 24.04 LTS. Практичный стартовый размер: 2 vCPU, 8 GB RAM и 50 GB balanced persistent disk.

Зарезервируйте статический внешний IPv4 и назначьте его `nic0`. Этот же адрес указывается как `PUBLIC_IP` в `.env`.

## Firewall

Разрешите входящий трафик:

| Protocol | Port(s) | Назначение |
|---|---:|---|
| TCP | 80 | HTTP redirect |
| TCP | 443 | Matrix client API, federation, Element, MAS, RTC signalling |
| TCP | 7881 | LiveKit TCP media fallback |
| UDP | 50000-50050 | LiveKit media |
| TCP | 22 | SSH; ограничить source IP |

PostgreSQL и Redis наружу не публикуются.

## Static IP

Не используйте ephemeral address. DNS и LiveKit должны опираться на стабильный публичный адрес.
