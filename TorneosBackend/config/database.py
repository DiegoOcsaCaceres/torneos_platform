"""
Gestión de la conexión a Neon.tech (PostgreSQL) via psycopg2.

Patrón: se expone obtener_conexion() que retorna una conexión psycopg2
con autocommit=False. Cada repositorio abre/cierra su propia conexión
para mantener transacciones independientes y evitar conexiones zombie.

La URL se guarda en la variable de entorno DATABASE_URL.
"""
import psycopg2
import psycopg2.extras  # RealDictCursor → filas como dict
from config.settings import DATABASE_URL


def obtener_conexion() -> psycopg2.extensions.connection:
    """
    Retorna una conexión activa a Neon.tech.

    Raises:
        EnvironmentError: Si DATABASE_URL no está configurada.
        RuntimeError:     Si la conexión falla.
    """
    if not DATABASE_URL:
        raise EnvironmentError(
            "Falta la variable de entorno DATABASE_URL. "
            "Revisa el archivo .env."
        )
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
        return conn
    except psycopg2.OperationalError as exc:
        raise RuntimeError(f"No se pudo conectar a la base de datos: {exc}") from exc
