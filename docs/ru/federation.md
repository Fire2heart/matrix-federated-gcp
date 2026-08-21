# Matrix federation

[English](../federation.md)

Федерация позволяет пользователям этого homeserver находиться в общих комнатах с пользователями других Matrix homeserver. Ручное связывание серверов не требуется.

В проекте Synapse resource `federation` включён всегда.

## Server name

По умолчанию:

```text
server_name = matrix.example.com
```

Matrix ID выглядит так:

```text
@alice:matrix.example.com
```

Такой вариант не требует отдельной инфраструктуры на apex-домене: клиентский API, федерация и `/.well-known/matrix/server` обслуживаются одним public endpoint.

## Порт 443

Synapse использует `serve_server_wellknown: true`. Endpoint:

```text
https://matrix.example.com/.well-known/matrix/server
```

сообщает другим homeserver использовать HTTPS 443. Отдельный внешний 8448 не требуется.

## Проверка

```bash
curl -fsS https://matrix.example.com/.well-known/matrix/server
curl -fsS https://matrix.example.com/_matrix/federation/v1/version
```

Hostname должен публично резолвиться в статический IP VM, а TCP 443 должен быть доступен из Internet.

## ID на apex-домене

Если нужны ID вида `@alice:example.com`, используется Matrix server-name delegation через `/.well-known/matrix/server` на apex-домене. Это следует выбрать до инициализации homeserver. `server_name` существующей установки менять нельзя.
