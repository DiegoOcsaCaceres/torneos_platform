"""
Script temporal de migración: agrega soporte para Torneo Relámpago
(eliminación directa) a las tablas existentes.
Se ejecuta una sola vez y luego se puede borrar.
"""
from config.database import obtener_conexion

SQL_MIGRACION = """
ALTER TABLE Partido ADD COLUMN IF NOT EXISTS fase VARCHAR(30);
ALTER TABLE Resultado ADD COLUMN IF NOT EXISTS penales_local INT;
ALTER TABLE Resultado ADD COLUMN IF NOT EXISTS penales_visita INT;
"""

def main():
    conn = obtener_conexion()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(SQL_MIGRACION)
        print("✅ Migración de Torneo Relámpago aplicada correctamente.")
    except Exception as exc:
        print(f"❌ Error al migrar: {exc}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()