ARG SYNAPSE_IMAGE
ARG MAS_IMAGE

FROM ${MAS_IMAGE} AS mas
FROM ${SYNAPSE_IMAGE}

USER root

COPY --from=mas /usr/local/bin/mas-cli /usr/local/bin/mas-cli
COPY --from=mas /usr/local/share/mas-cli/ /usr/local/share/mas-cli/

WORKDIR /opt/matrix-federated
COPY render.py ./render.py

LABEL org.opencontainers.image.description="Local configuration initializer for matrix-federated-gcp"

ENTRYPOINT ["python3", "/opt/matrix-federated/render.py"]
