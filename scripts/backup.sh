#!/usr/bin/env bash
# Script para respaldar la base de datos PostgreSQL de desarrollo que corre en Docker

# Detener ejecución ante cualquier error
set -euo pipefail

# Obtener la ruta absoluta del directorio del script para localizar el .env en la raíz
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

# Validar existencia de .env
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: El archivo .env no se encuentra en la raíz del proyecto." >&2
  exit 1
fi

# Cargar variables de entorno
set -a
source "$ENV_FILE"
set +a

# Validar variables necesarias para la conexión
for var in DB_USER DB_PASSWORD DB_NAME; do
  if [ -z "${!var:-}" ]; then
    echo "Error: La variable de entorno $var no está definida en el archivo .env" >&2
    exit 1
  fi
done

# Crear el directorio de backups si no existe
BACKUP_DIR="$SCRIPT_DIR/../backups"
mkdir -p "$BACKUP_DIR"

# Timestamp para el nombre del archivo
STAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${STAMP}.dump"

echo "Iniciando respaldo de la base de datos '$DB_NAME'..."

# Ejecutar pg_dump dentro del contenedor usando el formato custom (-Fc)
if ! docker exec -e PGPASSWORD="$DB_PASSWORD" bda_tp_final \
  pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "$BACKUP_FILE"; then
  echo "Error: Falló la ejecución de pg_dump en el contenedor." >&2
  # Eliminar archivo vacío si falló
  rm -f "$BACKUP_FILE"
  exit 1
fi

echo "Respaldo creado con éxito en: $BACKUP_FILE"
