# Matrix federation

[Русская версия](ru/federation.md)

Federation allows users on this homeserver to share rooms with users hosted on other Matrix homeservers. No manual server-to-server pairing is required.

This project enables the Synapse `federation` HTTP resource by default.

## Server name

The default installation uses:

```text
server_name = matrix.example.com
```

User IDs therefore look like:

```text
@alice:matrix.example.com
```

Using the Matrix hostname as `server_name` keeps deployment self-contained: the same public HAProxy endpoint serves client traffic, federation traffic and `/.well-known/matrix/server`.

## Port 443

Synapse is configured with `serve_server_wellknown: true`. The endpoint:

```text
https://matrix.example.com/.well-known/matrix/server
```

advertises federation on HTTPS port 443, so a separate public 8448 listener is not required.

## Validation

```bash
curl -fsS https://matrix.example.com/.well-known/matrix/server
curl -fsS https://matrix.example.com/_matrix/federation/v1/version
```

The hostname must resolve publicly to the VM static IP and TCP 443 must be reachable from the Internet.

## Optional apex-domain identities

If IDs such as `@alice:example.com` are required instead of `@alice:matrix.example.com`, use Matrix server-name delegation. This requires serving `/.well-known/matrix/server` on the apex domain and should be planned before the homeserver is initialized. Do not change `server_name` on an existing installation.
