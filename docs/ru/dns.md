# DNS

[English](../dns.md)

Создайте DNS-only записи на статический внешний IP VM в GCP.

Для `example.com`:

| Name | Type | Target |
|---|---|---|
| `matrix` | A | static IPv4 VM |
| `mas` | A | static IPv4 VM |
| `element` | A | static IPv4 VM |
| `rtc` | A | static IPv4 VM |
| `rtc-jwt` | A | static IPv4 VM |
| `panel` | A | static IPv4 VM; нужен при `COMPOSE_PROFILES=admin` |

Matrix endpoints должны резолвиться непосредственно в VM. LiveKit media ports не являются HTTP-трафиком.

Проверка:

```bash
dig +short matrix.example.com
dig +short element.example.com
dig +short rtc.example.com
```

В стандартном `.env.example` профиль `admin` включён. Если Element Admin и hostname `panel` не нужны, до deployment установите `COMPOSE_PROFILES=`.
