# Panel de Control de SGBD y Monitoreo de Recursos Masivos (IMDb)

##  Información Académica
**Institución:** Licenciatura en Ingeniería en Tecnologías de la Información e Innovación Digital (UTVAM)
**Materia:** Administración de Base de Datos
**Grupo:** IDS-801
**Docente:** Ing. Rubén Ramírez Gómez
**Fecha:** Junio, 2026

## Objetivo del Proyecto
Diseñar, implementar y documentar un monitor centralizado interactivo desarrollado en **Python / Streamlit** para Visualizar en tiempo real el consumo de recursos (CPU, RAM y Almacenamiento en Disco) de cinco Sistemas de Gestión de Bases de Datos (SGBD) corriendo de forma aislada en contenedores distribuidos de **Docker**. 

---

## SGBDs Soportados y Puertos Configurables
El monitor es agnóstico y modular, lo que permite auditar y gestionar múltiples tecnologías de bases de datos mediante parámetros configurables en su red virtual (`10.10.0.0/24`). El archivo `docker-compose.yml` contiene las siguientes imagenes y servicios:

1. **PostgreSQL 17 (Core Relacional):** Puerto Host: `5433` -> Puerto Contenedor: `5432` | IP: `10.10.0.4`
2. **MySQL Latest:** Puerto Host: `3308` -> Puerto Contenedor: `3306` | IP: `10.10.0.2`
3. **Microsoft SQL Server 2022:** Puerto Host: `1433` -> Puerto Contenedor: `1433` | IP: `10.10.0.3`
4. **MongoDB 4.4 (NoSQL Documental):** Puerto Host: `27017` -> Puerto Contenedor: `27017` | IP: `10.10.0.5`
5. **Cassandra Latest (NoSQL Columnar):** Puerto Host: `9042` -> Puerto Contenedor: `9042` | IP: `10.10.0.6`

---

## Requisitos del Sistema (En un Entorno Ubuntu)
Sistema Operativo: Ubuntu Linux (22.04 LTS o superior)
Python 3.14 o superior (instalado de forma explícita o mediante entorno aislado)
Docker Engine & Docker Compose V2 activos
Permisos de lectura/escritura sobre el Socket nativo de Docker (`/var/run/docker.sock`)

---

## Guía de Instalación Paso a Paso

### Paso 1: Clonar el Repositorio e ingresar

git clone [https://github.com/TU_USUARIO/Dashboard-Control-SGBD-IMDb.git](https://github.com/TU_USUARIO/Dashboard-Control-SGBD-IMDb.git)
cd Dashboard-Control-SGBD-IMDb

---

### Paso 2: Crear y activar el Entorno Virtual (Aislado)

Creamos un entorno virtual de Python, esto nos ayuda a  proteger las librerías del sistema operativo, en mi caso,  Ubuntu.

python3 -m venv .venv
source .venv/bin/activate'

--- 

## Paso 3: Instalar dependencias del Monitor

Instala los paquetes necesarios para la conexión transaccional con Postgres, comunicación con Docker y renderizado gráfico:
pip install streamlit docker pandas plotly psycopg2-binary

---

### Paso 4: Desbloquear los permisos del Socket de Docker

Para habilitar que el SDK de Python interactúe de forma nativa con Docker sin requerir privilegios de superusuario (sudo) en Streamlit, ejecuta:


sudo usermod -aG docker $USER
sudo chmod 666 /var/run/docker.sock

---

### Configuración del Monitor
El archivo dashboard_SGBD.py cuenta con un diccionario configurable llamado DB_PARAMS en su sección transaccional.
 estas líneas se pueden editar para adaptarlo a cualquier SGDB en el archivo Compose.yml o similar, el nombre varia pero el contenido debe de ser el de imagenes o servicios:

Python
DB_PARAMS = {
    "host": "localhost",
    "port": 5433,
    "database": "dbejemplo",    # Base de datos objetivo
    "user": "USUARIOPRINCIPAL", # Usuario administrador del SGBD
    "password": "root"          # Contraseña asignada
}