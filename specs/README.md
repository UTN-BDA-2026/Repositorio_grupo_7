# 📐 Specs — Trabajo Final (Grupo 7)

Este directorio contiene las **especificaciones** del trabajo final bajo un enfoque
**Spec-Driven Development (SDD)**: cada tarea se define primero como una spec
auto-contenida y recién después se implementa.

## ¿Por qué SDD acá?

1. **Repartir actividad real entre los integrantes.** Cada spec tiene un *owner*
   que la implementa, la documenta y la defiende. Así queda registrada en el
   repositorio la participación de cada uno (criterio de evaluación explícito).
2. **Trabajo en paralelo sin bloqueos.** Las specs están diseñadas para ser
   **independientes**: cada una toca archivos/áreas distintas, así nadie espera a
   que otro termine.

## Estado de cobertura de la consigna

La consigna pide implementar **al menos 4** de 7 temas. Estado objetivo del grupo:

| Tema | Estado | Dónde |
|---|---|---|
| ORM y/o Sin ORM | ✅ Hecho | `services/`, `database/transactions.py` |
| Seguridad | ✅ Hecho · 🔁 reforzado | `database/db.py` + **SPEC-03** |
| Transacciones | ✅ Hecho | `database/transactions.py` |
| **Índices** | 🟡 **SPEC-01** | modelos + Alembic |
| **Backup & Restore** | 🟡 **SPEC-02** | `scripts/` |
| **NoSQL** | 🟡 **SPEC-04** | `nosql/` |
| Particionado | ❌ No se implementa | — |

La aplicación que demuestra todo esto se construye en **SPEC-05** (UI).
Con SPEC-01, 02 y 04 implementadas el grupo cubre **6 de 7 temas**.

## Asignación de specs

| Spec | Tema | Owner | Rama | ¿Toca esquema BD? |
|---|---|---|---|---|
| [SPEC-01](SPEC-01-indices.md) | Índices | **Branko Almeira** | `feat/indexes` | ✅ (la única) |
| [SPEC-02](SPEC-02-backup-restore.md) | Backup & Restore | **Agustín Giorlando** | `feat/backup-restore` | ❌ |
| [SPEC-03](SPEC-03-seguridad-endurecimiento.md) | Seguridad (endurecimiento) | **Agustín Lara** | `feat/security-hardening` | ❌ |
| [SPEC-04](SPEC-04-nosql.md) | NoSQL | **Federico Sosa** | `feat/nosql-logging` | ❌ |
| [SPEC-05](SPEC-05-ui.md) | UI / demo de la app | **Branko Almeira** | `feat/dashboard-ui` | ❌ |

> **Lisandro Toledo** ya tiene actividad y **no ejecutará más código**: actúa
> exclusivamente como **revisor** de los PRs.
> *Los owners son una propuesta; ajústenla entre el grupo si hace falta.*

## Garantía de independencia (sin dependencias)

- **Solo SPEC-01 modifica el esquema** (genera una migración Alembic). Las demás
  trabajan sobre scripts, código de aplicación o un datastore NoSQL aparte.
- Por lo tanto **no hay conflictos de migración** ni de archivos entre specs.
- Cada spec arranca su rama desde `main` y se integra con su propio PR.

## Flujo de trabajo Git (metodología del grupo)

El grupo ya viene usando esta metodología; la mantenemos:

1. Ramas por funcionalidad con prefijo: `feat/*`, `fix/*`. **Nunca commit directo a `main`.**
2. **Conventional Commits**: `feat:`, `fix:`, `docs:`, `test:`, `chore:`.
3. Cada rama se integra a `main` mediante **Pull Request** revisado por Lisandro.
4. `main` siempre estable.

### Cada integrante, su propia identidad

Para que la actividad cuente por persona, antes de commitear configurá tu git:

```bash
git config user.name  "Tu Nombre"
git config user.email "tu-email-de-github@ejemplo.com"
```

Y arrancá tu rama desde `main` actualizado:

```bash
git checkout main && git pull
git checkout -b feat/<tu-rama>
```

## Plantilla de una spec

Todas las specs siguen la misma estructura estándar:
Contexto · Objetivo · Alcance / Fuera de alcance · Requisitos funcionales (RF) ·
Diseño técnico · Entregables · Criterios de aceptación (DoD) · Verificación ·
Plan de commits/PR · Notas para la defensa.
