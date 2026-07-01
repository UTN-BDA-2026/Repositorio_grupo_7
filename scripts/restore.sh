#!/usr/bin/env bash
# Script para restaurar la base de datos PostgreSQL de desarrollo que corre en Docker

# Detener ejecución ante cualquier error
set -euo pipefail

# Validar que se haya provisto el archivo de backup como argumento
if [ -z "${1:-}" ]; then
  echo "Error: Debe especificar el archivo de backup a restaurar." >&2
  echo "Uso: $0 <ruta_al_archivo.dump>" >&2
  exit 1
fi

BACKUP_FILE="$1"

# Validar que el archivo de backup exista
if [ ! -f "$BACKUP_FILE" ]; then
  echo "Error: El archivo de backup '$BACKUP_FILE' no existe o no es un archivo válido." >&2
  exit 1
fi

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

echo "Iniciando restauración de '$BACKUP_FILE' en la base de datos '$DB_NAME'..."

# Ejecutar pg_restore dentro del contenedor de Docker leyendo el archivo desde STDIN (-i)
# --clean: Elimina objetos antes de recrearlos.
# --if-exists: Evita errores al eliminar objetos que no existen previamente en la BD.
if ! docker exec -i -e PGPASSWORD="$DB_PASSWORD" bda_tp_final \
  pg_restore -U "$DB_USER" -d "$DB_NAME" --clean --if-exists < "$BACKUP_FILE"; then
  echo "Error: Falló la ejecución de pg_restore en el contenedor." >&2
  exit 1
fi

echo "Restauración completada con éxito."
