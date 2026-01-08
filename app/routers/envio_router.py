from fastapi import APIRouter, HTTPException, Header, status, Request
import jwt
import logging
from app.models.envio import Envio
from app.core.database import get_connection
from app.utils.sms import obtener_id_decode, obtener_id_encode

SECRET_KEY = "TU_LLAVE_SECRETA_CAMBIALA"

router = APIRouter(prefix="/api/envio", tags=["Envios"])

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


# ==========================
# VALIDACIÓN TOKEN
# ==========================
def verificar_token(authorization: str):
    if not authorization:
        logger.warning("Acceso sin token")
        raise HTTPException(status_code=401, detail="Token requerido")

    try:
        token = authorization.split(" ")[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded["user_id"]

    except Exception as e:
        logger.warning(f"Token inválido | error={repr(e)}")
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


# ==========================
# INSERTAR ENVIO (PROTEGIDO)
# ==========================
@router.post("/")
def insertar_envio(
    data: Envio,
    request: Request,
    authorization: str = Header(None)
):
    user_id = verificar_token(authorization)
    ip = request.client.host

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO envio_api (
                idcliente, fechaenvio, idtipo, urlaudio, texto, tipotelefono,
                prefijo, telefono, nombre, campo1, campo2,
                campo3, campo4, campo5, estado, fechaencola
            )
            OUTPUT INSERTED.IDENVIO
            VALUES (1, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, GETDATE())
        """

        values = (
            data.fechaenvio,
            data.urlaudio,
            data.texto,
            data.tipotelefono,
            data.prefijo,
            data.telefono,
            data.nombre,
            data.campo1,
            data.campo2,
            data.campo3,
            data.campo4,
            data.campo5
        )

        cursor.execute(sql, values)
        row = cursor.fetchone()

        if row is None:
            conn.rollback()
            logger.error("Insert fallido | No se obtuvo IDENVIO")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo obtener el id del registro insertado"
            )

        id_envio = row[0]
        conn.commit()

        logger.info(
            f"Envio insertado | idenvio={id_envio} | user_id={user_id} | ip={ip}"
        )

        idEnvio = obtener_id_encode(id_envio)

        return {
            "status": "ok",
            "message": "Registro insertado correctamente",
            "idenvio": idEnvio,
            "estado": 0
        }

    except Exception as e:
        logger.exception(
            f"Error insertando envio | user_id={user_id} | ip={ip}"
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


# ==========================
# OBTENER ENVIO (PROTEGIDO)
# ==========================
@router.get("/{idenvio}")
def obtener_envio(
    idenvio: str,
    request: Request,
    authorization: str = Header(None)
):
    user_id = verificar_token(authorization)
    ip = request.client.host

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql_encode = """ 
            select bdAuxsql.dbo.[DecodeDircon](?) as idenvio
        """
        cursor.execute(sql_encode, (str(idenvio),))
        result = cursor.fetchone()
        idenvio = int(result[0]) - 1000

        sql = """
            SELECT 
                bdAuxsql.dbo.CodeDircon(convert( int, idenvio + 1000)) AS IDENVIO,
                fechaenvio,
                fechaencola,
                fechahoraenvio,
                campo1 AS CodCentral,
                case when idtipo = 1 then 'SMS LARGO'
                WHEN idtipo = 2 THEN 'IVR'
                WHEN idtipo = 3 THEN 'SMS CORTO' END AS tipo,
                texto,
                tipotelefono,
                prefijo,
                telefono,
                estado
            FROM envio_api
            WHERE IDENVIO = ?
        """

        cursor.execute(sql, (idenvio,))
        row = cursor.fetchone()

        if not row:
            logger.warning(
                f"Envio no encontrado | idenvio={idenvio} | user_id={user_id} | ip={ip}"
            )
            raise HTTPException(status_code=404, detail="Registro no encontrado")

        columnas = [col[0] for col in cursor.description]
        data = dict(zip(columnas, row))

        logger.info(
            f"Consulta envio | idenvio={idenvio} | user_id={user_id} | ip={ip}"
        )

        return {
            "status": "ok",
            "data": data
        }

    except Exception as e:
        logger.exception(
            f"Error consultando envio | idenvio={idenvio} | user_id={user_id} | ip={ip}"
        )
        raise HTTPException(status_code=500, detail="Error interno del servidor")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.post("/envio-corto")
def insertar_envio_corto(
    data: Envio,
    request: Request,
    authorization: str = Header(None)
):
    user_id = verificar_token(authorization)
    ip = request.client.host

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO envio_api (
                idcliente, fechaenvio, idtipo, urlaudio, texto, tipotelefono,
                prefijo, telefono, nombre, campo1, campo2,
                campo3, campo4, campo5, estado, fechaencola
            )
            OUTPUT INSERTED.IDENVIO
            VALUES (1, ?, 3, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 5, GETDATE())
        """

        values = (
            data.fechaenvio,
            data.urlaudio,
            data.texto,
            data.tipotelefono,
            data.prefijo,
            data.telefono,
            data.nombre,
            data.campo1,
            data.campo2,
            data.campo3,
            data.campo4,
            data.campo5
        )

        cursor.execute(sql, values)
        row = cursor.fetchone()

        if row is None:
            conn.rollback()
            logger.error("Insert fallido | No se obtuvo IDENVIO")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo obtener el id del registro insertado"
            )

        id_envio = row[0]
        conn.commit()

        logger.info(
            f"Envio insertado | idenvio={id_envio} | user_id={user_id} | ip={ip}"
        )

        idEnvio = obtener_id_encode(id_envio)

        return {
            "status": "ok",
            "message": "Registro insertado correctamente",
            "idenvio": idEnvio,
            "estado": 0
        }

    except Exception as e:
        logger.exception(
            f"Error insertando envio | user_id={user_id} | ip={ip}"
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


@router.get("/envio-corto/{idenvio}")
def obtener_envio_corto(
    idenvio: str,
    request: Request,
    authorization: str = Header(None)
):
    user_id = verificar_token(authorization)
    ip = request.client.host

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql_encode = """ 
            select bdAuxsql.dbo.[DecodeDircon](?) as idenvio
        """
        cursor.execute(sql_encode, (str(idenvio),))
        result = cursor.fetchone()
        idenvio = int(result[0]) - 1000
        
        sql = """
            SELECT 
                bdAuxsql.dbo.CodeDircon(convert( int, idenvio + 1000)) AS IDENVIO,
                fechaenvio,
                fechaencola,
                fechahoraenvio,
                campo1 AS CodCentral,
                case when idtipo = 1 then 'SMS LARGO'
                WHEN idtipo = 2 THEN 'IVR'
                WHEN idtipo = 3 THEN 'SMS CORTO' END AS tipo,
                texto,
                tipotelefono,
                prefijo,
                telefono,
                estado
            FROM envio_api
            WHERE IDENVIO = ?
            AND estado = 5
        """

        cursor.execute(sql, (idenvio,))
        row = cursor.fetchone()

        if not row:
            logger.warning(
                f"Envio no encontrado | idenvio={idenvio} | user_id={user_id} | ip={ip}"
            )
            raise HTTPException(status_code=404, detail="Registro no encontrado")

        columnas = [col[0] for col in cursor.description]
        data = dict(zip(columnas, row))

        logger.info(
            f"Consulta envio | idenvio={idenvio} | user_id={user_id} | ip={ip}"
        )

        return {
            "status": "ok",
            "data": data
        }

    except Exception as e:
        logger.exception(
            f"Error consultando envio | idenvio={idenvio} | user_id={user_id} | ip={ip}"
        )
        raise HTTPException(status_code=500, detail="Error interno del servidor")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@router.post("/ivr")
def insertar_ivr(
    data: Envio,
    request: Request,
    authorization: str = Header(None)
):
    user_id = verificar_token(authorization)
    ip = request.client.host

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO envio_api (
                idcliente, fechaenvio, idtipo, urlaudio, texto, tipotelefono,
                prefijo, telefono, nombre, campo1, campo2,
                campo3, campo4, campo5, estado, fechaencola
            )
            OUTPUT INSERTED.IDENVIO
            VALUES (1, ?, 2, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, GETDATE())
        """

        values = (
            data.fechaenvio,
            data.urlaudio,
            data.texto,
            data.tipotelefono,
            data.prefijo,
            data.telefono,
            data.nombre,
            data.campo1,
            data.campo2,
            data.campo3,
            data.campo4,
            data.campo5
        )

        cursor.execute(sql, values)
        row = cursor.fetchone()

        if row is None:
            conn.rollback()
            logger.error("Insert fallido | No se obtuvo IDENVIO")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo obtener el id del registro insertado"
            )

        id_envio = row[0]
        conn.commit()

        logger.info(
            f"Envio insertado | idenvio={id_envio} | user_id={user_id} | ip={ip}"
        )

        idEnvio = obtener_id_encode(id_envio)

        return {
            "status": "ok",
            "message": "Registro insertado correctamente",
            "idenvio": idEnvio,
            "estado": 0
        }

    except Exception as e:
        logger.exception(
            f"Error insertando envio | user_id={user_id} | ip={ip}"
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

@router.get("/ivr/{idenvio}")
def obtener_ivr(
    idenvio: str,
    request: Request,
    authorization: str = Header(None)
):
    user_id = verificar_token(authorization)
    ip = request.client.host

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql_encode = """ 
            select bdAuxsql.dbo.[DecodeDircon](?) as idenvio
        """
        cursor.execute(sql_encode, (str(idenvio),))
        result = cursor.fetchone()
        idenvio = int(result[0]) - 1000
        
        sql = """
            SELECT 
                bdAuxsql.dbo.CodeDircon(convert( int, idenvio + 1000)) AS IDENVIO,
                fechaenvio,
                fechaencola,
                fechahoraenvio,
                campo1 AS CodCentral,
                case when idtipo = 1 then 'SMS LARGO'
                WHEN idtipo = 2 THEN 'IVR'
                WHEN idtipo = 3 THEN 'SMS CORTO' END AS tipo,
                texto,
                tipotelefono,
                prefijo,
                telefono,
                estado
            FROM envio_api
            WHERE IDENVIO = ? 
        """

        cursor.execute(sql, (idenvio,))
        row = cursor.fetchone()

        if not row:
            logger.warning(
                f"Envio no encontrado | idenvio={idenvio} | user_id={user_id} | ip={ip}"
            )
            raise HTTPException(status_code=404, detail="Registro no encontrado")

        columnas = [col[0] for col in cursor.description]
        data = dict(zip(columnas, row))

        logger.info(
            f"Consulta envio | idenvio={idenvio} | user_id={user_id} | ip={ip}"
        )

        return {
            "status": "ok",
            "data": data
        }

    except Exception as e:
        logger.exception(
            f"Error consultando envio | idenvio={idenvio} | user_id={user_id} | ip={ip}"
        )
        raise HTTPException(status_code=500, detail="Error interno del servidor")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()