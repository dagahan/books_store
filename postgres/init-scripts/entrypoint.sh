#!/bin/bash
set -e

envsubst < /init-scripts/init-template.sql > /init-scripts/init.sql

cp /init-scripts/init.sql /docker-entrypoint-initdb.d/init.sql

exec docker-entrypoint.sh postgres "$@"