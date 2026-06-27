## Encendido del Entorno y Monitor

1. Abre una terminal en Ubuntu y dirígete a la carpeta raíz del proyecto.
2. Activa tu entorno virtual:
   source .venv/bin/activate

Ejecuta el comando de arranque del monitor:
streamlit run dashboard_SGBD.py

se debe de abrir en el navegador automáticamente el Dashboard en la dirección local http://localhost:8501.

2. Gestión de la Infraestructura Docker (Sección 1)
Arranque Masivo: Haz clic en el botón,  Levantar TODOS los Contenedores para encender los 5 manejadores al mismo tiempo en segundo plano.

Arranque Individual: Usa los botones de tipo Switch debajo del nombre de cada SGBD. Si el indicador marca Apagado, haz clic en Encender (Serivicio) para cambiar su estado en tiempo real a  Corriendo o Encendido.

Liberación de Memoria: Al finalizar la práctica, haz clic en  Apagar TODOS los Contenedores para liberar la RAM asignada (hasta 7GB combinados en límites de Compose).

3. Monitoreo de Recursos en Tiempo Real (Sección 2)
Las gráficas interactivas se actualizan al refrescar la pantalla:

Gráfica de RAM: Muestra cuántos megabytes (MB) consume de forma neta cada motor activo.

Gráfica de Almacenamiento (GB): Demuestra visualmente cómo el contenedor de PostgreSQL lidera el consumo de almacenamiento con más de 2 GB de datos persistidos, debido al proceso de normalización e inyección masiva de los millones de registros de IMDb, mientras que los otros manejadores se conservan vacíos como plantillas base (0.35 GB) ya que no se les cargo informacion .