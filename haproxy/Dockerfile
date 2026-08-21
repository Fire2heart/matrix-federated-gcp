FROM haproxy:3.4.3

USER root

COPY haproxy-main.cfg /usr/local/etc/haproxy/haproxy.cfg
COPY entrypoint.sh /usr/local/bin/my-matrix-haproxy-entrypoint

RUN chmod 0555 /usr/local/bin/my-matrix-haproxy-entrypoint

ENTRYPOINT ["/usr/local/bin/my-matrix-haproxy-entrypoint"]
