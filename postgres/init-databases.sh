#!/bin/sh
set -eu

# EN: Create isolated application roles/databases inside one PostgreSQL instance.
# RU: Создаёт изолированные роли/базы приложений в одном экземпляре PostgreSQL.
: "${SYNAPSE_DB_USER:?SYNAPSE_DB_USER is required}"
: "${SYNAPSE_DB_PASSWORD:?SYNAPSE_DB_PASSWORD is required}"
: "${SYNAPSE_DB_NAME:?SYNAPSE_DB_NAME is required}"
: "${MAS_DB_USER:?MAS_DB_USER is required}"
: "${MAS_DB_PASSWORD:?MAS_DB_PASSWORD is required}"
: "${MAS_DB_NAME:?MAS_DB_NAME is required}"

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=synapse_user="$SYNAPSE_DB_USER" \
  --set=synapse_password="$SYNAPSE_DB_PASSWORD" \
  --set=synapse_db="$SYNAPSE_DB_NAME" \
  --set=mas_user="$MAS_DB_USER" \
  --set=mas_password="$MAS_DB_PASSWORD" \
  --set=mas_db="$MAS_DB_NAME" <<'EOSQL'
CREATE ROLE :"synapse_user" LOGIN PASSWORD :'synapse_password';
CREATE DATABASE :"synapse_db"
  OWNER :"synapse_user"
  ENCODING 'UTF8'
  LC_COLLATE 'C'
  LC_CTYPE 'C'
  TEMPLATE template0;
REVOKE ALL ON DATABASE :"synapse_db" FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE :"synapse_db" TO :"synapse_user";

CREATE ROLE :"mas_user" LOGIN PASSWORD :'mas_password';
CREATE DATABASE :"mas_db"
  OWNER :"mas_user"
  ENCODING 'UTF8'
  LC_COLLATE 'C'
  LC_CTYPE 'C'
  TEMPLATE template0;
REVOKE ALL ON DATABASE :"mas_db" FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE :"mas_db" TO :"mas_user";
EOSQL

echo "[postgres-init] Synapse and MAS databases created"
