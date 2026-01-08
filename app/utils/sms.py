from fastapi import HTTPException,  status
from app.core.database import get_connection
import logging


# ==========================
# CONFIGURACIÓN DEL LOGGER
# ==========================
logger = logging.getLogger("envio_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/envio.log", encoding="utf-8")
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)

def obtener_id_encode(idenvio):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        encod = int(idenvio) + 1000

        sql = """
            SELECT bdAuxsql.dbo.CodeDircon(?) AS IDENVIO
        """
        cursor.execute(sql, (encod,))
        row = cursor.fetchone()

    except Exception as e:
        logger.exception(
            f"Error insertando envio | idenvio={idenvio} | "
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return row[0]

def obtener_id_decode():
    pass