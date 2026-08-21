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
| `panel` | A | static IPv4 VM, optional |

Matrix endpoints должны резолвиться непосредственно в VM. LiveKit media ports не являются HTTP-трафиком.

Проверка:

```bash
dig +short matrix.example.com
dig +short element.example.com
dig +short rtc.example.com
```
