"""
Script temporal de migración: agrega la columna 'formato' a Torneo,
para distinguir entre Liga (round-robin) y Torneo Relámpago (eliminación
directa). Se ejecuta una sola vez y luego se puede borrar.
"""
from config.database import obtener_conexion

SQL_MIGRACION = """
ALTER TABLE Torneo ADD COLUMN IF NOT EXISTS formato VARCHAR(20) DEFAULT 'liga';
"""

def main():
    conn = obtener_conexion()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(SQL_MIGRACION)
        print("✅ Migración de formato de Torneo aplicada correctamente.")
    except Exception as exc:
        print(f"❌ Error al migrar: {exc}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()