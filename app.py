import streamlit as st
import psycopg2

# Configuración de la página del Dashboard
st.set_page_config(page_title="Dashboard Cómputo - RBAC", layout="wide")
st.title(" Dashboard de Inventario - Control de Acceso (RBAC)")


DB_CONFIG = {
    "host": "localhost",
    "database": "tienda_computo2",
    "port": "5433"
}


st.sidebar.header("Control de Sesión")
rol_app = st.sidebar.selectbox("Selecciona tu Rol de Usuario:", ["Usuario Normal", "Administrador"])


if rol_app == "Administrador":
    user_bd = "rol_admin"
    pass_bd = "secure_admin_pass"
else:
    user_bd = "rol_normal"
    pass_bd = "secure_user_pass"

# Función centralizada para conectarse y ejecutar sentencias SQL
def ejecutar_query(query, es_dml=False):
    conn = None
    resultado = None
    columnas = []
    error_msg = None
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            port=DB_CONFIG["port"],
            user=user_bd,
            password=pass_bd
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(query)
        
        # Si no es una operación de escritura (DML) y tiene filas que retornar
        if not es_dml and cur.description:
            resultado = cur.fetchall()
            columnas = [desc[0] for desc in cur.description]
        cur.close()
    except Exception as e:
        error_msg = str(e)
    finally:
        if conn:
            conn.close()
    return resultado, columnas, error_msg

# 2. Interfaz de Botones de Operaciones
st.header("Operaciones de Inventario")
col1, col2, col3, col4 = st.columns(4)

with col1:
    btn_select = st.button("Ver Artículos (SELECT)", use_container_width=True)
with col2:
    btn_insert = st.button("Insertar Registro (INSERT)", use_container_width=True)
with col3:
    btn_update = st.button("Modificar Registro (UPDATE)", use_container_width=True)
with col4:
    btn_delete = st.button(" Eliminar Registro (DELETE)", use_container_width=True)

# Lógica al presionar el botón SELECT (Permitido para ambos roles)
if btn_select:
    res, cols, err = ejecutar_query("SELECT id, nombre, categoria, precio, stock FROM articulos ORDER BY id;")
    if err:
        st.error(f"Error de base de datos: {err}")
    else:
        st.subheader("Catálogo de Artículos (Vista Autorizada)")
        st.dataframe(res, column_config={i: cols[i] for i in range(len(cols))})

# Bloqueo estricto en la UI para operaciones DML si el usuario es "Normal"
if btn_insert or btn_update or btn_delete:
    if rol_app == "Usuario Normal":
        st.error("No cuentas con permisos DML, contacta al administrador del sistema.")
    else:
        st.success(" Acción DML autorizada. Utilice la consola inferior para procesar comandos arbitrarios como Admin.")

# 3. Despliegue de la Query Console Exclusiva para el Administrador
if rol_app == "Administrador":
    st.write("---")
    st.header(" Admin Query Console")
    st.caption("Consola interactiva SQL libre ejecutándose con privilegios altos (`rol_admin`)")
    
    # Textarea donde el administrador puede escribir cualquier query (DML, DDL, DCL)
    query_usuario = st.text_area(
        "Escribe tu consulta SQL aquí (Ej. GRANT / REVOKE / INSERT / UPDATE):", 
        value="SELECT * FROM articulos;"
    )
    btn_ejecutar = st.button("⚡ Ejecutar Query en Consola", type="primary")
    
    if btn_ejecutar:
        # Detectamos si la query incluye palabras clave de escritura o permisos
        es_query_dml = any(keyword in query_usuario.upper() for keyword in ["INSERT", "UPDATE", "DELETE", "GRANT", "REVOKE"])
        res, cols, err = ejecutar_query(query_usuario, es_dml=es_query_dml)
        
        if err:
            st.error(f" Error de ejecución en consola: {err}")
        else:
            st.success("Sentencia procesada en la base de datos con éxito.")
            # Si fue una consulta de lectura dentro de la consola, mostramos los datos devueltos
            if not es_query_dml and res is not None:
                st.dataframe(res)