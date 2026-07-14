"""
Script temporal de migración: agrega la columna 'jugadores_por_equipo' a Torneo,
para que la cantidad de jugadores por equipo configurada al crear el torneo
quede persistida en el backend (antes solo vivía en localStorage del navegador
que creó el torneo, por lo que en cualquier otra máquina se veía el valor por
defecto). Se ejecuta una sola vez y luego se puede borrar.
"""
from config.database import obtener_conexion

SQL_MIGRACION = """
ALTER TABLE Torneo ADD COLUMN IF NOT EXISTS jugadores_por_equipo INT DEFAULT 5;
"""

def main():
    conn = obtener_conexion()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(SQL_MIGRACION)
        print("✅ Migración de jugadores_por_equipo en Torneo aplicada correctamente.")
    except Exception as exc:
        print(f"❌ Error al migrar: {exc}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
