# HAProxy

[Русская версия](ru/haproxy-container.md)

HAProxy publishes TCP 80 and 443 and routes requests by hostname to Docker services. Matrix client API and federation share the `matrix.<domain>` virtual host. TLS certificates are read from the shared `haproxy_certs` volume populated by acme.sh.
