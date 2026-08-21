# Архитектура

[English](../architecture.md)

- HAProxy — единственная HTTP/HTTPS точка входа, TCP 80/443.
- Synapse обслуживает client API и federation через HAProxy.
- MAS отвечает за authentication.
- Element Web — браузерный клиент.
- LiveKit + lk-jwt-service обеспечивают MatrixRTC.
- PostgreSQL и Redis находятся только во внутренних Docker networks.
- acme.sh получает wildcard certificate через Cloudflare DNS-01.
- LiveKit публикует TCP 7881 и UDP media range непосредственно на VM.
