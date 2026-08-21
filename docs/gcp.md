# Google Cloud deployment

[Русская версия](ru/gcp.md)

## VM

Create a Compute Engine VM with Ubuntu 24.04 LTS. A practical initial size is 2 vCPU, 8 GB RAM and a 50 GB balanced persistent disk.

Reserve a static external IPv4 and attach it to `nic0`. The same address is written to `PUBLIC_IP` in `.env`.

## Firewall

Allow inbound traffic to the VM:

| Protocol | Port(s) | Purpose |
|---|---:|---|
| TCP | 80 | HTTP redirect / operational access |
| TCP | 443 | Matrix client API, federation, Element, MAS, RTC signalling |
| TCP | 7881 | LiveKit TCP media fallback |
| UDP | 50000-50050 | LiveKit media |
| TCP | 22 | SSH administration; restrict source addresses |

The Docker databases and Redis are never published on the VM network interface.

## Static IP

Do not use an ephemeral external address. DNS records and LiveKit media advertisement depend on a stable address.

After the VM is created, confirm the assigned address before generating `.env`.
