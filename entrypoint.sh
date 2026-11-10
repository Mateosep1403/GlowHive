#!/bin/sh
set -e

# Solo el contenedor web prepara la base de datos y los estáticos.
if [ "$RUN_MIGRATIONS" = "1" ]; then
  echo "[entrypoint] Aplicando migraciones..."
  until python manage.py migrate --noinput; do
    echo "[entrypoint] DB no lista, reintentando en 2s..."; sleep 2
  done
  python manage.py collectstatic --noinput
  if [ "$SEED_DATA" = "1" ]; then python manage.py poblar_datos || true; fi
fi

exec "$@"