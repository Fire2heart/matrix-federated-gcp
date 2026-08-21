ARG SYNAPSE_IMAGE=matrixdotorg/synapse:v1.157.1
ARG MAS_IMAGE=ghcr.io/element-hq/matrix-authentication-service:1.21.0

FROM ${MAS_IMAGE} AS mas
FROM ${SYNAPSE_IMAGE}

USER root
COPY --from=mas /usr/local/bin/mas-cli /usr/local/bin/mas-cli
COPY --from=mas /usr/local/share/mas-cli/ /usr/local/share/mas-cli/
COPY render.py /opt/my_matrix/render.py
RUN chmod 0755 /opt/my_matrix/render.py

LABEL org.opencontainers.image.description="Configuration initializer for the my_matrix Docker Compose stack"

ENTRYPOINT ["python3", "/opt/my_matrix/render.py"]
