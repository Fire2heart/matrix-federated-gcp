# Portainer

[English](../portainer.md)

Portainer необязателен. Reference deployment использует Docker Compose напрямую на VM. Если используется Portainer, deploy должен идти из Git repository, чтобы Compose видел build contexts `./config-image` и `./haproxy`. Сгенерированный `.env` загрузите в environment variables стека. Credentials собственного container registry не нужны.
