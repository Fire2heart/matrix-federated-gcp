# HAProxy

[English](../haproxy-container.md)

HAProxy публикует TCP 80/443 и маршрутизирует запросы по hostname к Docker services. Matrix client API и federation используют `matrix.<domain>`. TLS certificate читается из общего volume `haproxy_certs`, который обновляет acme.sh.
