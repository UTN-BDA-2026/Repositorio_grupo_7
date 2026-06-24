# 🤖 Instructivo — OpenCode + cómo avanzar tu spec

Esta guía explica cómo instalar **OpenCode** (agente de IA para la terminal,
open-source) y cómo cada integrante usa su **prompt** para implementar la spec que
tiene asignada bajo el flujo Spec-Driven Development.

> Cada uno trabaja **su** spec, en **su** rama, con **su** identidad de git. Las specs
> son independientes (ver `specs/README.md`): no se pisan entre sí.

---

## 1. ¿Qué es OpenCode?

OpenCode es un agente de IA que corre en la terminal y trabaja sobre el repositorio:
lee archivos, escribe código, ejecuta comandos y te ayuda a implementar tu spec.
Sitio: <https://opencode.ai> · Repo: <https://github.com/sst/opencode>

## 2. Instalación

Elegí **una** de estas opciones según tu sistema.

### Opción A — Script de instalación (Linux / macOS / WSL) — recomendada
```bash
curl -fsSL https://opencode.ai/install | bash
```

### Opción B — npm (cualquier SO con Node 18+)
```bash
npm install -g opencode-ai
```

### Opción C — Homebrew (macOS / Linux)
```bash
brew install sst/tap/opencode
```

### Windows
Usá **WSL** (Ubuntu) y seguí la Opción A, o instalá Node y usá la Opción B.

### Verificar la instalación
```bash
opencode --version
```
Si el comando no se encuentra, cerrá y reabrí la terminal (para recargar el `PATH`).

## 3. Configurar el proveedor de IA (autenticación)

OpenCode necesita un modelo. Configurá tu proveedor (Anthropic/Claude, OpenAI, etc.):
```bash
opencode auth login
```
Seguí las instrucciones (vas a pegar una API key o loguearte). Una vez hecho, queda
guardado para las próximas sesiones.

## 4. Abrir el proyecto

```bash
cd /ruta/a/Repositorio_grupo_7
opencode
```
Esto abre la interfaz de OpenCode dentro del repo. Para salir: `Ctrl+C` o `/exit`.

## 5. Antes de empezar: tu identidad y tu rama

**Importante** para que tu actividad cuente como tuya en GitHub. Configurá tu git
(una sola vez) y creá tu rama desde `main` actualizado:

```bash
git config user.name  "Tu Nombre"
git config user.email "tu-email-de-github@ejemplo.com"

git checkout main && git pull
git checkout -b feat/<tu-rama>     # ver la rama en specs/README.md
```

| Integrante | Spec | Rama |
|---|---|---|
| Branko Almeira | SPEC-01 Índices | `feat/indexes` |
| Branko Almeira | SPEC-05 UI | `feat/dashboard-ui` (ya existe; `git checkout feat/dashboard-ui`) |
| Agustín Giorlando | SPEC-02 Backup & Restore | `feat/backup-restore` |
| Agustín Lara | SPEC-03 Seguridad | `feat/security-hardening` |
| Federico Sosa | SPEC-04 NoSQL | `feat/nosql-logging` |

## 6. Levantar el entorno (una vez por máquina)

```bash
cp .env.example .env                 # si todavía no lo tenés
docker compose up -d                 # Postgres en Docker
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head                 # crea las tablas
```
> En Debian/Ubuntu, si `venv` falla: `sudo apt install python3-venv`.

## 7. Pegá tu prompt en OpenCode

Copiá el prompt de tu spec (sección 8) y pegalo en OpenCode. El agente va a leer tu
spec, implementarla respetando el alcance y dejar todo listo para tu PR.

## 8. Prompts por integrante

> Pegá **solo** el bloque que te corresponde.

### 🟦 Branko — SPEC-01 (Índices)
```
Vas a implementar specs/SPEC-01-indices.md. Primero leé specs/README.md y esa spec
completa. Implementá EXACTAMENTE lo que pide: los 8 índices en los modelos SQLAlchemy
(__table_args__), generá la migración Alembic, el script de seed para benchmark y el
documento docs/indices.md con EXPLAIN ANALYZE antes/después. Respetá el "Fuera de
alcance": NO toques otras áreas ni otras specs. Usá Conventional Commits según el
"Plan de commits". Verificá todos los Criterios de aceptación antes de terminar.
No commitees ni pushees sin avisarme.
```

### 🟦 Branko — SPEC-05 (UI)
```
Vas a implementar specs/SPEC-05-ui.md (continúa la rama feat/dashboard-ui que ya tiene
base). Leé specs/README.md y esa spec completa. Construí las vistas (POS, productos,
clientes, historial, dashboard) delegando SIEMPRE en services/ y en
database/transactions.py (sin SQL en la UI). Respetá el "Fuera de alcance". Seguí el
"Plan de commits" con Conventional Commits y verificá los Criterios de aceptación.
No commitees ni pushees sin avisarme.
```

### 🟩 Agustín Giorlando — SPEC-02 (Backup & Restore)
```
Vas a implementar specs/SPEC-02-backup-restore.md. Leé specs/README.md y esa spec
completa. Creá scripts/backup.sh y scripts/restore.sh con pg_dump/pg_restore leyendo
.env (sin credenciales hardcodeadas), agregá backups/ al .gitignore y documentá en
docs/backup_restore.md. Respetá el "Fuera de alcance": NO toques el esquema ni el
código de la app. Probá el ciclo backup→restore. Conventional Commits y verificá los
Criterios de aceptación. No commitees ni pushees sin avisarme.
```

### 🟨 Agustín Lara — SPEC-03 (Seguridad)
```
Vas a implementar specs/SPEC-03-seguridad-endurecimiento.md. Leé specs/README.md y esa
spec completa. Agregá services/security.py (hash/verify con bcrypt), integralo en
user_service, hacé configurable sslmode en database/db.py, actualizá .env.example y
requirements.txt, sumá tests/test_security.py y documentá docs/seguridad.md. Respetá
el "Fuera de alcance": NO cambies el esquema. Conventional Commits y verificá los
Criterios de aceptación (incluido pytest en verde). No commitees ni pushees sin avisarme.
```

### 🟧 Federico Sosa — SPEC-04 (NoSQL)
```
Vas a implementar specs/SPEC-04-nosql.md. Leé specs/README.md y esa spec completa.
Agregá el servicio mongo a docker-compose.yml, creá el módulo nosql/ (client.py,
events.py) con pymongo leyendo .env, enganchá log_event al confirmar la venta de forma
BEST-EFFORT (que NO rompa la transacción si Mongo falla), actualizá .env.example y
requirements.txt y documentá docs/nosql.md justificando la decisión. Respetá el
"Fuera de alcance". Conventional Commits y verificá los Criterios de aceptación.
No commitees ni pushees sin avisarme.
```

## 9. Cerrar tu tarea

1. Revisá la checklist de **Criterios de aceptación (DoD)** de tu spec: deben estar todos ✅.
2. Commiteá con Conventional Commits y pusheá tu rama.
3. Abrí un **Pull Request** contra `main` y pedile la revisión a **Lisandro**.
4. En el PR, mencioná qué spec cubre (ej: "Implementa SPEC-02").

---

### Reglas de oro

- Trabajá **solo** tu spec. Si necesitás algo de otra área, avisá al grupo.
- No mezcles credenciales en el código (siempre `.env`).
- Si el agente quiere salirse del alcance de tu spec, frenalo.
