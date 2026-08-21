FROM haproxy:3.4.3

USER root

COPY haproxy-main.cfg /usr/local/etc/haproxy/haproxy.cfg
COPY entrypoint.sh /usr/local/bin/matrix-federated-haproxy-entrypoint

RUN chmod 0555 /usr/local/bin/matrix-federated-haproxy-entrypoint

ENTRYPOINT ["/usr/local/bin/matrix-federated-haproxy-entrypoint"]
