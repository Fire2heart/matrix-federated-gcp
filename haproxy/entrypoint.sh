#!/bin/sh
set -eu

CONFIG=/usr/local/etc/haproxy/haproxy.cfg
CERT=/etc/haproxy/certs/haproxy.pem

# EN: HAProxy must not start before ACME has produced a usable certificate.
# RU: HAProxy не должен стартовать, пока ACME не создаст рабочий сертификат.

while [ ! -s "$CERT" ]; do
    echo "[haproxy] waiting for TLS certificate: $CERT"
    sleep 2
done

# EN: Validate before starting the master/worker process.
# RU: Проверяем config перед запуском master/worker процесса.
haproxy -c -f "$CONFIG"

haproxy -W -db -f "$CONFIG" &
haproxy_pid=$!

terminate() {
    trap - TERM INT
    if kill -0 "$haproxy_pid" 2>/dev/null; then
        kill -TERM "$haproxy_pid" 2>/dev/null || true
    fi
    wait "$haproxy_pid" 2>/dev/null || true
    exit 0
}

trap terminate TERM INT

# EN: Watch the certificate file and gracefully reload workers after renewal.
# RU: Следим за сертификатом и делаем graceful reload workers после renewal.
cert_mtime=$(stat -c %Y "$CERT" 2>/dev/null || echo 0)

while kill -0 "$haproxy_pid" 2>/dev/null; do
    sleep 30 &
    wait $! || true

    new_mtime=$(stat -c %Y "$CERT" 2>/dev/null || echo 0)
    if [ "$new_mtime" != "$cert_mtime" ] && [ "$new_mtime" != "0" ]; then
        echo "[haproxy] TLS certificate changed; validating configuration"
        if haproxy -c -f "$CONFIG"; then
            echo "[haproxy] reloading workers"
            kill -USR2 "$haproxy_pid"
            cert_mtime=$new_mtime
        else
            echo "[haproxy] configuration validation failed; keeping current workers" >&2
        fi
    fi
done

wait "$haproxy_pid"
