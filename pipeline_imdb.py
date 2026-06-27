import psycopg2
import os
import time
import subprocess

# Configuración de conexión al contenedor de PostgreSQL
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "user": "USUARIOPRINCIPAL",
    "password": "root",
    "database": "dbejemplo"
}

def verificar_tabla_existente(cursor, nombre_tabla):
    """Verifica si una tabla ya existe en la base de datos y contiene datos"""
    try:
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{nombre_tabla}'
            );
        """)
        existe = cursor.fetchone()[0]
        if existe:
            cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla} LIMIT 1;")
            tiene_datos = cursor.fetchone()[0] > 0
            return tiene_datos
        return False
    except:
        return False

def ejecutar_pipeline():
    print("🚀 Iniciando Pipeline Automatizado de Estandarización IMDb...")
    start_total = time.time()
    
    try:
        # Conexión formal a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True  
        cursor = conn.cursor()
        
        # Lista de tablas definitivas esperadas
        tablas_definitivas = [
            "name_basics", "name_known_for_titles", 
            "title_basics", "title_genres", "title_principals"
        ]
        
        # Comprobar si TODAS las tablas ya están procesadas y tienen registros
        ya_procesado = all(verificar_tabla_existente(cursor, t) for t in tablas_definitivas)
        
        if ya_procesado:
            print("\n🔍 [INFO] Se detectó que las tablas definitivas ya contienen los datos estandarizados.")
            print("⏩ Saltando la fase de procesamiento y carga masiva...")
        else:
            print("\n🔄 No se detectaron todas las tablas limpias. Iniciando procesamiento masiva...")
            
            # =====================================================================
            # 1. PROCESAMIENTO DE LA TABLA: name.basics.tsv
            # =====================================================================
            print("\n🔹 Procesando 'name.basics.tsv'...")
            cursor.execute("DROP TABLE IF EXISTS staging_name_basics CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS name_basics CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS name_known_for_titles CASCADE;")
            
            cursor.execute("""
                CREATE UNLOGGED TABLE staging_name_basics (
                    nconst TEXT, primaryName TEXT, birthYear TEXT, deathYear TEXT, 
                    primaryProfession TEXT, knownForTitles TEXT
                );
            """)
            cursor.execute("""
                COPY staging_name_basics FROM '/shared/name.basics.tsv' 
                DELIMITER E'\t' CSV HEADER QUOTE E'\b' NULL '\\N';
            """)
            cursor.execute("""
                CREATE TABLE name_basics (
                    name_id INT PRIMARY KEY,
                    primary_name VARCHAR(255),
                    birth_year INT,
                    death_year INT,
                    primary_profession VARCHAR(255)[]
                );
            """)
            print("   -> Estandarizando y migrando a tabla definitiva...")
            cursor.execute("""
                INSERT INTO name_basics
                SELECT CAST(SUBSTRING(nconst, 3) AS INT), NULLIF(primaryName, '\\N'),
                       NULLIF(birthYear, '\\N')::INT, NULLIF(deathYear, '\\N')::INT,
                       string_to_array(NULLIF(primaryProfession, '\\N'), ',')::VARCHAR[]
                FROM staging_name_basics ON CONFLICT DO NOTHING;
            """)
            cursor.execute("""
                CREATE TABLE name_known_for_titles (
                    name_id INT, title_id INT, PRIMARY KEY (name_id, title_id)
                );
            """)
            cursor.execute("""
                INSERT INTO name_known_for_titles
                SELECT CAST(SUBSTRING(nconst, 3) AS INT),
                       CAST(SUBSTRING(unnest(string_to_array(knownForTitles, ',')), 3) AS INT)
                FROM staging_name_basics WHERE knownForTitles <> '\\N' AND knownForTitles IS NOT NULL
                ON CONFLICT DO NOTHING;
            """)
            cursor.execute("DROP TABLE IF EXISTS staging_name_basics;")
            print("   ✅ Tabla 'name.basics' estandarizada con éxito.")

            # =====================================================================
            # 2. PROCESAMIENTO DE LA TABLA: title.basics.tsv
            # =====================================================================
            print("\n🔹 Procesando 'title.basics.tsv'...")
            cursor.execute("DROP TABLE IF EXISTS staging_title_basics CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS title_basics CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS title_genres CASCADE;")
            
            cursor.execute("""
                CREATE UNLOGGED TABLE staging_title_basics (
                    tconst TEXT, titleType TEXT, primaryTitle TEXT, originalTitle TEXT,
                    isAdult TEXT, startYear TEXT, endYear TEXT, runtimeMinutes TEXT, genres TEXT
                );
            """)
            cursor.execute("""
                COPY staging_title_basics FROM '/shared/title.basics.tsv' 
                DELIMITER E'\t' CSV HEADER QUOTE E'\b' NULL '\\N';
            """)
            cursor.execute("""
                CREATE TABLE title_basics (
                    title_id INT PRIMARY KEY, title_type VARCHAR(50), primary_title TEXT,
                    original_title TEXT, is_adult BOOLEAN, start_year INT, end_year INT, runtime_minutes INT
                );
            """)
            print("   -> Estandarizando y migrando a tabla definitiva...")
            cursor.execute("""
                INSERT INTO title_basics
                SELECT CAST(SUBSTRING(tconst, 3) AS INT), NULLIF(titleType, '\\N'),
                       NULLIF(primaryTitle, '\\N'), NULLIF(originalTitle, '\\N'),
                       CASE WHEN isAdult = '1' THEN TRUE ELSE FALSE END,
                       NULLIF(startYear, '\\N')::INT, NULLIF(endYear, '\\N')::INT, NULLIF(runtimeMinutes, '\\N')::INT
                FROM staging_title_basics ON CONFLICT DO NOTHING;
            """)
            cursor.execute("""
                CREATE TABLE title_genres (
                    title_id INT, genre VARCHAR(100), PRIMARY KEY (title_id, genre)
                );
            """)
            cursor.execute("""
                INSERT INTO title_genres
                SELECT CAST(SUBSTRING(tconst, 3) AS INT), unnest(string_to_array(genres, ','))
                FROM staging_title_basics WHERE genres <> '\\N' AND genres IS NOT NULL
                ON CONFLICT DO NOTHING;
            """)
            cursor.execute("DROP TABLE IF EXISTS staging_title_basics;")
            print("   ✅ Tabla 'title.basics' estandarizada con éxito.")

            # =====================================================================
            # 3. PROCESAMIENTO DE LA TABLA: title.principals.tsv
            # =====================================================================
            print("\n🔹 Procesando 'title.principals.tsv'...")
            cursor.execute("DROP TABLE IF EXISTS staging_title_principals CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS title_principals CASCADE;")
            
            cursor.execute("""
                CREATE UNLOGGED TABLE staging_title_principals (
                    tconst TEXT, ordering TEXT, nconst TEXT, category TEXT, job TEXT, characters TEXT
                );
            """)
            cursor.execute("""
                COPY staging_title_principals FROM '/shared/title.principals.tsv' 
                DELIMITER E'\t' CSV HEADER QUOTE E'\b' NULL '\\N';
            """)
            cursor.execute("""
                CREATE TABLE title_principals (
                    title_id INT, ordering INT, name_id INT, category VARCHAR(100), job TEXT, characters TEXT[],
                    PRIMARY KEY (title_id, ordering)
                );
            """)
            print("   -> Estandarizando y migrando a tabla definitiva...")
            cursor.execute("""
                INSERT INTO title_principals
                SELECT CAST(SUBSTRING(tconst, 3) AS INT), CAST(ordering AS INT), CAST(SUBSTRING(nconst, 3) AS INT),
                       NULLIF(category, '\\N'), NULLIF(job, '\\N'),
                       CASE WHEN characters = '\\N' OR characters IS NULL THEN NULL 
                            ELSE string_to_array(regexp_replace(characters, '[\\[\\]" ]', '', 'g'), ',') END::TEXT[]
                FROM staging_title_principals ON CONFLICT DO NOTHING;
            """)
            cursor.execute("DROP TABLE IF EXISTS staging_title_principals;")
            print("   ✅ Tabla 'title.principals' estandarizada con éxito.")

        # Cerrar cursores antes de lanzar comandos del sistema
        cursor.close()
        conn.close()
        
        # =====================================================================
        # 4. ETAPA AUTOMÁTICA DE COMPRESIÓN (EXPORTACIÓN ORO)
        # =====================================================================
        print("\n📦 Iniciando fase de exportación y compresión masiva...")
        
        ruta_salida = os.path.expanduser("~/Documentos/Universidad/Ruben 8vo/datasets_limpios")
        os.makedirs(ruta_salida, exist_ok=True)  # <-- CORREGIDO: exist_ok=True listo!
        
        for tabla in tablas_definitivas:
            print(f"   -> Comprimiendo y guardando '{tabla}'...")
            comando = f"sudo docker exec -i postgresql_container psql -p 5432 -U USUARIOPRINCIPAL -d dbejemplo -c \"COPY {tabla} TO STDOUT WITH CSV HEADER\" | gzip > \"{ruta_salida}/{tabla}_clean.csv.gz\""
            subprocess.run(comando, shell=True, check=True)
            
        end_total = time.time()
        print(f"\n🎉 ¡Pipeline Completado con Éxito en {round(end_total - start_total, 2)} segundos!")
        print(f"📂 Tus 5 archivos optimizados (.csv.gz) te esperan listos en:\n   {ruta_salida}")

    except Exception as e:
        print(f"\n❌ Error crítico durante la ejecución del pipeline: {e}")

if __name__ == "__main__":
    ejecutar_pipeline()