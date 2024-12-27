#!/bin/bash
set -e

echo "shared_preload_libraries = 'pg_cron'" >> "${PGDATA}/postgresql.conf"
echo "cron.database_name = 'postgres'" >> "${PGDATA}/postgresql.conf"
echo "cron.use_background_workers = on" >> "${PGDATA}/postgresql.conf"
