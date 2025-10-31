# Dashboard Dinámico con Dash y MariaDB

Este proyecto es una aplicación web de dashboard multi-página construida con el framework **Dash** de Python. La aplicación se conecta a una base de datos MariaDB y ofrece dos vistas principales:

1. **Tablas Dinámicas (`/`):** Una página que **se genera automáticamente** leyendo la base de datos conectada. Muestra una tabla interactiva para *cada* tabla encontrada, implementando paginación, ordenación y filtrado del lado del servidor.
2. **Dashboard Principal (`/dashboard`):** Una página con 8 visualizaciones interactivas (mapa de coropletas, gráficos de barras, gráficos circulares y de dispersión) basadas en la base de datos `world` de ejemplo.

---

## 🚀 Características Principales

* **Dashboard Interactivo:** 8 gráficos de Plotly que visualizan datos de población, geografía, economía e idiomas del mundo.
* **Página de Tablas Dinámica:** Se adapta automáticamente a cualquier esquema de base de datos. Si cambias la conexión a una base de datos `employees`, mostrará las tablas `employees`, `departments`, etc.
* **Alto Rendimiento (Server-Side):** Toda la paginación y filtrado de las tablas se realiza en el servidor (en la base de datos) usando `LIMIT`, `OFFSET`, `ORDER BY` y `WHERE`. Esto asegura que la aplicación sea rápida y escalable.
* **Conexión Eficiente:** Utiliza SQLAlchemy para gestionar un pool de conexiones a la base de datos, mejorando el rendimiento.
* **Configuración Segura:** Las credenciales de la base de datos se gestionan de forma segura fuera del código fuente mediante un archivo `.env` (gracias a `python-dotenv`).

---

## 🔧 Configuración y Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto localmente.

### 1. Prerrequisitos

* Python 3.8 o superior.
* Una instancia de MariaDB (o MySQL) en ejecución.
* El archivo `world.sql` proporcionado.

### 2. Instalación

1.  **Clonar el repositorio** (o descargar los archivos en un directorio):
    ```bash
    git clone https://github.com/Jhon0507/DashboardOfWorld.git
    cd DashboardOfWorld
    ```

2.  **Crear y activar un entorno virtual:**
    * En Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * En macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instalar las dependencias:**
    Instala todos los paquetes de `requirements.txt` con el siguiente comando:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuración de la Base de Datos

1.  **Cargar los Datos:** Importa el archivo `world.sql` en tu instancia de MariaDB. Esto creará la base de datos `world` y sus tablas, necesarias para que funcione el dashboard principal.

2.  **Crear archivo `.env`:**
    En la raíz de tu proyecto (junto a `app.py`), crea un archivo llamado `.env` y añade tus credenciales. Sustituye los valores de ejemplo por los tuyos:

    ```dotenv
    # Credenciales de la Base de Datos
    HOST=127.0.0.1
    PORT=3307
    NAME=world
    USER=tu_usuario_mariadb
    PASSWORD=tu_contraseña_secreta
    ```
    * **Nota:** Si quieres probar la funcionalidad dinámica, puedes cambiar `DB_NAME` a otra base de datos (ej. `employees`) después de ejecutar la app por primera vez. La página `/` se adaptará, pero la página `/dashboard` mostrará errores (ya que depende de las tablas `city`, `country`, etc.).

### 4. Ejecución

1.  Asegúrate de que tu entorno virtual esté activado.
2.  Ejecuta la aplicación principal:
    ```bash
    python app.py
    ```
3.  Abre tu navegador y ve a: **http://localhost:8050/**

---
## 🛠️ Tecnologías Utilizadas

* **Backend & Visualización:** Dash (Plotly)
* **Manipulación de Datos:** Pandas
* **Base de Datos:** MariaDB
* **Conexión a BD:** SQLAlchemy (con el conector `mariadb`)
* **Gestión de Entorno:** `python-dotenv`