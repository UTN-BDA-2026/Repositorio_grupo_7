# 💾 Estrategia de Backup & Restore (SPEC-02)

Este documento describe el diseño, la justificación y las instrucciones de uso para la estrategia de respaldos (backup) y restauración (restore) de la base de datos de desarrollo.

---

## 🏗️ Estrategia y Diseño Técnico

Para evitar que los desarrolladores necesiten tener instaladas localmente las herramientas cliente de PostgreSQL (`pg_dump` y `pg_restore`) y asegurar la compatibilidad entre distintos sistemas operativos, la estrategia consiste en ejecutar las herramientas nativas **dentro del contenedor de Docker de la base de datos (`bda_tp_final`)** utilizando el comando `docker exec`.

### 1. Formato de Respaldo Custom (`-Fc`) vs Texto Plano (`.sql`)
Hemos elegido el formato **Custom (`-Fc`)** provisto por PostgreSQL por las siguientes ventajas clave:
*   **Compresión integrada:** El formato custom comprime automáticamente los datos, reduciendo significativamente el espacio en disco del dump.
*   **Restauración selectiva:** Permite reordenar o filtrar los elementos a restaurar (por ejemplo, restaurar solo una tabla específica o solo el esquema) mediante `pg_restore`.
*   **Portabilidad y robustez:** Evita problemas de sintaxis y codificación comunes al ejecutar scripts `.sql` planos de gran tamaño.

### 2. Seguridad en las Credenciales
Para cumplir con las directrices de seguridad y evitar la exposición de credenciales hardcodeadas:
*   Las credenciales de acceso a la base de datos (`DB_USER`, `DB_PASSWORD`, `DB_NAME`) se extraen directamente del archivo `.env` en la raíz del proyecto.
*   El script exporta de manera temporal la variable de entorno `PGPASSWORD` para que los comandos de Postgres se autentiquen automáticamente de forma no interactiva, sin exponer la contraseña en la línea de comandos (donde sería visible en procesos del sistema mediante comandos como `ps`).

---

## 📋 Requisitos Previos

1.  Tener Docker y Docker Compose instalados y en ejecución.
2.  Contar con un entorno compatible con Bash (por ejemplo, Git Bash en Windows, WSL o Linux/macOS).
3.  Tener configurado el archivo `.env` en la raíz del repositorio con variables válidas:
    ```env
    DB_USER=admin
    DB_PASSWORD=admin1234
    DB_NAME=dba_final
    ```

---

## 🚀 Instrucciones de Uso

### 1. Crear un respaldo (Backup)
Ejecuta el script de backup desde la raíz del proyecto:
```bash
bash scripts/backup.sh
```

**¿Qué hace el script?**
1.  Valida la existencia del archivo `.env` y que las variables requeridas estén presentes.
2.  Crea la carpeta `backups/` en la raíz (la cual está agregada al `.gitignore` para evitar subir dumps a GitHub).
3.  Ejecuta `pg_dump` dentro del contenedor `bda_tp_final`.
4.  Genera un archivo con la fecha y hora de creación, por ejemplo: `backups/dba_final_20260627_224500.dump`.

---

### 2. Restaurar un respaldo (Restore)
Para restaurar un archivo de backup en la base de datos de desarrollo, ejecuta el script de restauración pasando la ruta del archivo `.dump` como argumento:
```bash
bash scripts/restore.sh backups/nombre_del_archivo.dump
```

**¿Qué hace el script?**
1.  Comprueba que se haya ingresado el archivo y que este exista.
2.  Carga las credenciales del `.env`.
3.  Ejecuta `pg_restore` dentro del contenedor `bda_tp_final` usando las banderas:
    *   `--clean`: Elimina (drop) los objetos de la base de datos (tablas, índices, secuencias, etc.) antes de volver a crearlos, asegurando que no haya conflictos de duplicación.
    *   `--if-exists`: Evita que el script falle con errores si intenta eliminar objetos que aún no existen en la base de datos vacía.

---

## ⚠️ Consideraciones para Windows
Si estás utilizando Windows y recibes un error de permisos o formato de fin de línea al ejecutar los scripts en Bash:
*   Asegúrate de ejecutar los comandos en **Git Bash** o **WSL**.
*   Si los archivos `.sh` se crearon con saltos de línea de Windows (CRLF), puedes convertirlos a formato Unix (LF) utilizando un editor de texto (como VS Code, seleccionando `LF` en la esquina inferior derecha) o con la herramienta `dos2unix`.
