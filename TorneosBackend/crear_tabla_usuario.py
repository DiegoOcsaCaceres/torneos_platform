"""
Script temporal de migración: crea la tabla Usuario en la base de datos.
Se ejecuta una sola vez y luego se puede borrar.
"""
from config.database import obtener_conexion

SQL_CREAR_USUARIO = """
CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombres VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'ORGANIZADOR',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro TIMESTAMP NOT NULL DEFAULT NOW()
);
"""

def main():
    conn = obtener_conexion()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(SQL_CREAR_USUARIO)
        print("✅ Tabla 'Usuario' creada correctamente (o ya existía).")
    except Exception as exc:
        print(f"❌ Error al crear la tabla: {exc}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()