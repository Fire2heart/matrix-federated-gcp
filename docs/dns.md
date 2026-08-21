# DNS

[Русская версия](ru/dns.md)

Create DNS-only records pointing to the GCP VM static external IP.

For `example.com`:

| Name | Type | Target |
|---|---|---|
| `matrix` | A | VM static IPv4 |
| `mas` | A | VM static IPv4 |
| `element` | A | VM static IPv4 |
| `rtc` | A | VM static IPv4 |
| `rtc-jwt` | A | VM static IPv4 |
| `panel` | A | VM static IPv4, optional |

Use direct DNS records for the Matrix endpoints. LiveKit media ports do not pass through an HTTP CDN proxy.

Check:

```bash
dig +short matrix.example.com
dig +short element.example.com
dig +short rtc.example.com
```

All required names should return the VM static address.
