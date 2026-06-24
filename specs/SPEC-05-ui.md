# SPEC-05 — Interfaz de escritorio (CustomTkinter)

| Campo | Valor |
|---|---|
| **Owner** | Branko Almeira |
| **Rama** | `feat/dashboard-ui` (continúa la existente) |
| **Estado** | Borrador |
| **Tema de la consigna** | Aplicación / demo del trabajo (interfaz monolítica de escritorio) |
| **Dependencias** | **Ninguna para arrancar** (consume `services/` que ya está en `main`). Integra el resto de los temas a medida que se mergean. |
| **Fecha** | 2026-06-24 |

---

## 1. Contexto

La rama `feat/dashboard-ui` ya tiene una **base** construida con CustomTkinter
(`ui/app.py`, ~144 líneas): contenedor principal, menú lateral (sidebar), soporte de
**modo claro/oscuro**, botones de escalado (`A+`/`A-`) y tarjetas de resumen. Falta
conectar las vistas a la base de datos y construir las pantallas funcionales.

Branko toma la titularidad de esta rama y la lleva a una **demo funcional** que sirva
para la defensa. (Lisandro, autor de la base, ya no ejecuta más código.)

## 2. Objetivo

Completar una aplicación de escritorio funcional que permita **demostrar en vivo** el
trabajo: registrar una venta (que usa la transacción SQL nativa), gestionar productos
y clientes (CRUD vía la capa de servicios/ORM) y ver el historial de ventas.

## 3. Alcance (in scope)

- Estructura modular de UI: `ui/app.py` (shell) + `ui/views/` (pantallas) + `ui/components/` (widgets reutilizables).
- **Vista de Ventas (POS):** seleccionar productos, armar el carrito, confirmar venta
  llamando a `database.transactions.process_sale_transaction`.
- **Vista de Productos / Inventario:** listar y dar de alta/baja/modificación usando `services/product_service.py`.
- **Vista de Clientes:** ABM básico vía `services/client_service.py`.
- **Vista de Historial de Ventas:** tabla de ventas registradas.
- **Dashboard:** tarjetas de resumen con datos reales (totales del día, stock bajo, etc.).
- Conexión a la BD a través de la **capa de servicios existente** (no SQL directo en la UI).

## 4. Fuera de alcance (out of scope)

- Sistema de permisos/roles.
- Reportes avanzados / exportaciones.
- Empaquetado/instalador (`.exe`). La demo corre con `python main.py`.
- Re-implementar lógica de negocio en la UI (debe delegar en `services/` y `transactions.py`).

## 5. Requisitos funcionales

| RF | Descripción |
|---|---|
| RF-1 | La app arranca con `python main.py` y muestra el shell con sidebar y navegación entre vistas. |
| RF-2 | **POS:** el usuario busca productos (por nombre o código de barra), los agrega a un carrito y confirma la venta; se invoca `process_sale_transaction` y se muestra éxito/error. |
| RF-3 | Si la venta falla (p. ej. stock insuficiente), la UI muestra el error y **no** queda registro parcial (la transacción hace rollback). |
| RF-4 | **Productos:** listar, crear, editar y desactivar productos usando `product_service`. |
| RF-5 | **Clientes:** alta y listado de clientes usando `client_service`. |
| RF-6 | **Historial:** tabla con las ventas registradas (id, fecha, total, cliente). |
| RF-7 | **Dashboard:** al menos 2 tarjetas con datos reales consultados a la BD. |
| RF-8 | La UI **nunca** arma SQL: siempre llama a `services/` o a `transactions.py`. |

## 6. Diseño técnico

### 6.1 Estructura

```
ui/
├── __init__.py
├── app.py            # shell: ventana, sidebar, router de vistas (ya existe, refactor)
├── components/       # widgets reutilizables (tabla, formulario, input de búsqueda)
└── views/
    ├── dashboard_view.py
    ├── pos_view.py
    ├── products_view.py
    ├── clients_view.py
    └── sales_history_view.py
```

### 6.2 Acceso a datos

La UI obtiene una sesión con `database.db.get_db()` / `SessionLocal` y la pasa a los
servicios (`ProductService(db)`, etc.). Para la venta usa directamente
`process_sale_transaction(sale_data, details_data)`.

### 6.3 Patrón de vistas

Cada vista es un `CTkFrame` que el shell muestra/oculta al navegar. Las operaciones
de BD se hacen en handlers de botones; los errores se muestran en un diálogo/label.

## 7. Entregables

- `ui/app.py` refactorizado como shell + router.
- `ui/views/*.py` (las 5 vistas).
- `ui/components/*.py` (widgets reutilizables que surjan).
- `main.py` lanzando la app.
- `docs/ui.md` con capturas y guía de la demo.

## 8. Criterios de aceptación (Definition of Done)

- [ ] `python main.py` abre la app sin errores.
- [ ] Se puede **registrar una venta completa** desde la UI y queda en la BD (verificable en psql).
- [ ] Una venta con stock insuficiente muestra error y no deja registro parcial.
- [ ] Productos y clientes se pueden listar y crear desde la UI.
- [ ] El historial muestra las ventas registradas.
- [ ] La UI no contiene SQL embebido (solo usa `services/` y `transactions.py`).
- [ ] `docs/ui.md` con capturas. PR aprobado.

## 9. Plan de verificación

1. `docker compose up -d` + `alembic upgrade head` + datos mínimos (productos, sucursal, usuario, cliente).
2. `python main.py` → navegar por las vistas.
3. Registrar una venta → confirmar en psql que aparece en `sales`/`sale_details` y que bajó el stock en `branch_product`.
4. Probar venta con stock insuficiente → ver el error y confirmar que no hay registro parcial.

## 10. Plan de commits / PR

```
refactor: separar app.py en shell + router de vistas
feat: vista POS que registra ventas con la transaccion nativa
feat: vista de productos (CRUD) usando product_service
feat: vista de clientes y vista de historial de ventas
feat: dashboard con tarjetas de datos reales
docs: guia de la demo con capturas
```
PR: **"feat: UI funcional (dashboard + POS + ABM)"** → base `main`.

## 11. Notas para la defensa

- Por qué **interfaz monolítica** (CustomTkinter) y no una API + frontend (decisión ya
  documentada en el README: evitar mantener APIs).
- Cómo la UI **delega** en la capa de servicios (ORM) y en la transacción nativa, sin
  mezclar SQL en la presentación (separación de responsabilidades).
- Mostrar en vivo el **rollback**: una venta con stock insuficiente que no deja rastro.
- Es la pieza que **integra y demuestra** el resto de los temas (transacciones, ORM,
  y —al mergearse— índices, seguridad y NoSQL).
