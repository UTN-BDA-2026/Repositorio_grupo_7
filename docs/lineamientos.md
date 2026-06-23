# Documento de Arquitectura y Lineamientos del Proyecto

## 1. Stack Tecnológico Seleccionado

| Capa | Tecnología |
|---|---|
| **Lenguaje** | Python 3.x |
| **Interfaz Gráfica (GUI)** | CustomTkinter — enfoque estructurado/POO para interfaces de escritorio modernas |
| **Motor de Base de Datos** | PostgreSQL — elegido por su robustez transaccional y soporte de índices avanzados |
| **Gestión de BD (ORM)** | SQLAlchemy — ORM estándar de la industria en Python, modo sincrónico |
| **Conexión Nativa (Driver)** | `psycopg3` en modo sincrónico — para ejecución de SQL puro en bloques críticos |
| **Migraciones** | Alembic — herramienta de migraciones para SQLAlchemy |
| **Config** | `python-dotenv` — gestión de variables de entorno desde archivo `.env` |



## 2. Requerimientos de la Cursada Implementados

El desarrollo cumplirá con los enunciados de la materia implementando una **arquitectura híbrida** que aborda los siguientes 4 pilares:

### I. ORM y/o Sin ORM (Enfoque Mixto)

Se implementa una arquitectura que combina ambos enfoques, optimizando la productividad y el control:

- **ORM (SQLAlchemy):** Se utilizará para la definición de modelos (clases Python que mapean tablas), la sincronización de la base de datos entre entornos mediante Alembic y las operaciones CRUD básicas (ABM de clientes, productos, etc.).

- **Sin ORM (SQL Nativo):** Se utilizará mediante `psycopg3` para procesos de negocio críticos y complejos, garantizando un control absoluto sobre el motor de la base de datos, la gestión de transacciones explícitas y el rendimiento de ejecución.

### II. Transacciones

Se implementará control transaccional explícito (`BEGIN`, `COMMIT`, `ROLLBACK`) mediante SQL Nativo con `psycopg3` en los módulos de operaciones compuestas.

- **Caso de uso principal:** Confirmación de comprobantes o ventas. La inserción de la cabecera, la iteración sobre el detalle de los artículos y el descuento del stock se ejecutarán como una operación atómica. Cualquier violación de restricción (ej. stock negativo) disparará un `ROLLBACK` total capturado por la interfaz.

### III. Seguridad

Se establecen tres capas de seguridad obligatorias:

- **Gestión de Credenciales:** Prohibición estricta de variables hardcodeadas. Las cadenas de conexión se almacenarán en un archivo `.env` local, gestionado a través de `python-dotenv` y excluido del control de versiones mediante `.gitignore`.

- **Prevención de Inyección SQL:** Toda consulta ejecutada mediante `psycopg3` utilizará estrictamente paso de parámetros (consultas parametrizadas). Nunca se construirán queries por concatenación de strings.

- **ORM Seguro:** SQLAlchemy sanitiza por defecto las entradas en todas las operaciones estándar.

### IV. Índices

Se diseñarán índices específicos, adicionales a las Claves Primarias (PK) y Foráneas (FK) generadas por defecto, para optimizar las cargas de lectura en la aplicación.

- **Implementación:** Declarados en los modelos de SQLAlchemy mediante `Index()` dentro de `__table_args__`.

- **Caso de uso principal:** Se aplicarán sobre columnas de búsqueda frecuente en la interfaz gráfica, como el DNI de clientes, códigos de barra o rangos de fechas en las tablas de facturación.

---

## 3. Sincronización y Entornos (Migraciones con Alembic)

Para resolver el versionado de la base de datos entre los distintos equipos (ej. laboratorio de la facultad vs. equipos personales), se **prohíbe** el intercambio manual de scripts `.sql` aislados.

- Los modelos SQLAlchemy son la **única fuente de verdad** de la estructura de la base de datos.
- Cualquier cambio estructural requiere la generación de una migración mediante Alembic (`alembic revision --autogenerate`).
- Al descargar los cambios del repositorio, cada integrante ejecutará `alembic upgrade head` para aplicar las migraciones pendientes en su motor local.

---

## 4. Estructura de Directorios (Propuesta)

La separación de responsabilidades (UI vs. Lógica de Datos) es estricta para evitar acoplamiento.

```
proyecto_db/
│
├── .env       # Variables de entorno locales
├── .gitignore # Exclusión de venv, .env, __pycache__, etc.
├── requirements.txt # Dependencias
│
├── alembic/# Configuración y scripts de migración
│   ├── env.py
│   └── versions/ # Archivos de migración generados automáticamente
│
├── database/
│   ├── __init__.py
│   ├── connection.py #de SQLAlchemy y sesiones (lee del .env)
│   ├── models.py # Definición de tablas
│   └── transactions.py #transacciones SQL nativas (psycopg3)
│
├── ui/
│   ├── __init__.py
│   ├── app.py # Ventana principal (CustomTkinter)
│   ├── components/ # Widgets modulares (tablas, inputs, etc)
│   └── views/ # Vistas principales (ABM, pantalla de operaciones)
│
└── main.py # Punto de entrada de la aplicación
```

---

## 5. Dependencias (`requirements.txt`)

```
customtkinter
sqlalchemy
psycopg3
alembic
python-dotenv
```

---

## 6. Roadmap y Estado Actual de la Interfaz

**✅ Lo que hemos implementado hasta ahora:**
*   **Estructura Base del Dashboard:** Construcción del contenedor principal (`ui/app.py`) con CustomTkinter.
*   **Navegación:** Menú lateral (Sidebar) preparado para conectar con las distintas vistas.
*   **Accesibilidad y Tema:** Soporte completo nativo para **Modo Claro / Modo Oscuro** y botones de escalado de la interfaz (`A+` / `A-`).
*   **Tarjetas de Resumen:** Área de datos elevada con colores vibrantes y de alto contraste.

**⏳ Próximos pasos (Siguiente Sesión):**
1.  **Dashboard (Continuación):** Integrar los gráficos estadísticos en el área inferior mediante Matplotlib.
2.  **Pantalla de Autenticación:** Desarrollar la **Ventana de Login** para validar el ingreso de usuarios antes de mostrar el Dashboard.
3.  **Vistas Modulares:** Separar y construir las pantallas individuales de:
    *   **Ventas:** Pantalla tipo POS (Punto de Venta) para la facturación.
    *   **Historial / Transacciones:** Tabla de registros de las ventas realizadas.
    *   **Gestión de Productos/Inventario.**
4.  **Conexión UI-BD:** Enlazar las vistas con SQLAlchemy y los modelos correspondientes.
