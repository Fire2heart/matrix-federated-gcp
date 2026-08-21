# Portainer

[Русская версия](ru/portainer.md)

Portainer is optional. The reference deployment uses Docker Compose directly on the VM. If Portainer is used, deploy from the Git repository so the relative build contexts `./config-image` and `./haproxy` are available to Compose. Load the generated `.env` as stack environment variables. No project-owned container registry credentials are required.
