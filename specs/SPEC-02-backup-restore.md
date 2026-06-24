# SPEC-02 — Backup & Restore

| Campo | Valor |
|---|---|
| **Owner** | Agustín Giorlando |
| **Rama** | `feat/backup-restore` |
| **Estado** | Borrador |
| **Tema de la consigna** | Backup & Restore (scripts/tarea para restaurar la DB de desarrollo) |
| **Dependencias** | **Ninguna** (no toca el esquema ni el código de la app) |
| **Fecha** | 2026-06-24 |

---

## 1. Contexto

Hoy no hay forma reproducible de respaldar ni restaurar la base. La consigna pide
"mediante scripts o tarea que permita restaurar la DB de desarrollo". La base corre
en un contenedor Docker (`bda_tp_final`, Postgres 17) definido en `docker-compose.yml`,
y las credenciales viven en `.env`.

## 2. Objetivo

Proveer scripts simples y seguros para **respaldar** y **restaurar** la base de
desarrollo, leyendo la configuración desde `.env` (sin credenciales hardcodeadas) y
funcionando contra el contenedor Docker existente.

## 3. Alcance (in scope)

- Script de **backup** con `pg_dump` (formato custom `-Fc`).
- Script de **restore** con `pg_restore` (con `--clean --if-exists`).
- Lectura de credenciales desde `.env`.
- Funcionar tanto con `pg_dump` local como vía `docker exec` (elegir un enfoque y documentarlo).
- Documentación de uso en `docs/backup_restore.md`.

## 4. Fuera de alcance (out of scope)

- Backups automáticos programados (cron) en producción.
- Almacenamiento remoto (S3, etc.).
- Cambios en el esquema o en el código de la aplicación.

## 5. Requisitos funcionales

| RF | Descripción |
|---|---|
| RF-1 | `scripts/backup.sh` genera un dump con timestamp en el nombre, dentro de `backups/` (carpeta ignorada por git). |
| RF-2 | El dump usa formato **custom** (`pg_dump -Fc`) para permitir restore selectivo y compresión. |
| RF-3 | `scripts/restore.sh <archivo>` restaura un dump sobre la base de desarrollo, recreando objetos (`--clean --if-exists`). |
| RF-4 | Ambos scripts leen `DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME` desde `.env` (vía `set -a; source .env; set +a` o `export`). |
| RF-5 | Si falta una variable o el dump no existe, el script falla con mensaje claro (`set -euo pipefail`). |

## 6. Diseño técnico

Enfoque recomendado: ejecutar `pg_dump`/`pg_restore` **dentro del contenedor** con
`docker exec` (así no hay que instalar el cliente de Postgres en cada máquina).

Forma general (adaptar, no copiar literal):

```bash
# backup.sh
set -euo pipefail
set -a; source .env; set +a
mkdir -p backups
STAMP=$(date +%Y%m%d_%H%M%S)
docker exec -e PGPASSWORD="$DB_PASSWORD" bda_tp_final \
  pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "backups/${DB_NAME}_${STAMP}.dump"
```

```bash
# restore.sh
set -euo pipefail
[ -f "${1:-}" ] || { echo "Uso: restore.sh <archivo.dump>"; exit 1; }
set -a; source .env; set +a
docker exec -i -e PGPASSWORD="$DB_PASSWORD" bda_tp_final \
  pg_restore -U "$DB_USER" -d "$DB_NAME" --clean --if-exists < "$1"
```

> **Seguridad:** pasar la contraseña por `PGPASSWORD` (variable de entorno), nunca en
> la línea de comando visible. Nada de credenciales en el código.

Agregar a `.gitignore`: `backups/`.

## 7. Entregables

- `scripts/backup.sh`
- `scripts/restore.sh`
- Línea `backups/` en `.gitignore`.
- `docs/backup_restore.md` con instrucciones de uso y la estrategia elegida.

## 8. Criterios de aceptación (Definition of Done)

- [ ] `bash scripts/backup.sh` genera un `.dump` en `backups/`.
- [ ] `bash scripts/restore.sh backups/<archivo>.dump` restaura la base sin errores.
- [ ] Prueba de ciclo completo: backup → borrar una tabla a mano → restore → la tabla vuelve.
- [ ] Ninguna credencial aparece hardcodeada en los scripts.
- [ ] `backups/` está ignorado por git.
- [ ] `docs/backup_restore.md` explica cómo usarlo. PR aprobado.

## 9. Plan de verificación

1. `docker compose up -d` y `alembic upgrade head` (base con tablas).
2. `bash scripts/backup.sh` → verificar archivo en `backups/`.
3. Borrar/alterar datos en una tabla con psql.
4. `bash scripts/restore.sh backups/<archivo>` → verificar que los datos volvieron.

## 10. Plan de commits / PR

```
feat: script de backup con pg_dump leyendo .env
feat: script de restore con pg_restore
chore: ignorar carpeta backups/
docs: documentar estrategia de backup & restore
```
PR: **"feat: backup & restore"** → base `main`.

## 11. Notas para la defensa

- Diferencia entre formato **plano (`.sql`)** y **custom (`-Fc`)**, y por qué el custom
  permite restore selectivo y compresión.
- Por qué `--clean --if-exists` en el restore.
- Cómo se mantienen las credenciales fuera del código (`.env` + `PGPASSWORD`).
- Qué se respalda (datos + esquema) y cómo se relaciona con Alembic (esquema versionado
  vs respaldo de datos).
