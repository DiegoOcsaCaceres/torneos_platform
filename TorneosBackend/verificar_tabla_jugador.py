"""
Script temporal: verifica si la tabla Jugador existe en la BD.
Se puede borrar después de usarlo.
"""
from config.database import obtener_conexion

def main():
    conn = obtener_conexion()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'jugador'
                    ORDER BY ordinal_position;
                """)
                columnas = cur.fetchall()
                if not columnas:
                    print("❌ La tabla 'Jugador' NO existe en la base de datos.")
                else:
                    print("✅ La tabla 'Jugador' SÍ existe. Columnas:")
                    for col in columnas:
                        print(f"   - {col['column_name']} ({col['data_type']})")
    finally:
        conn.close()

if __name__ == '__main__':
    main()