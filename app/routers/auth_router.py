from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from app.core.database import get_connection
import logging
import os

# ===============================
# CONFIGURACIÓN LOGGER
# ===============================

LOG_PATH = "logs"
LOG_FILE = "auth.log"

os.makedirs(LOG_PATH, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_PATH, LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("auth_logger")

# ===============================
# CONFIG JWT
# ===============================

SECRET_KEY = "TU_LLAVE_SECRETA_CAMBIALA"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8

# ===============================
# ROUTER
# ===============================

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# ===============================
# MODELS
# ===============================

class LoginRequest(BaseModel):
    email: str
    password: str

# ===============================
# ENDPOINT LOGIN
# ===============================

@router.post("/login")
def login(data: LoginRequest, request: Request):
    conn = None
    cursor = None
    ip_cliente = request.client.host

    logger.info(f"Intento de login | email={data.email} | ip={ip_cliente}")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT idcliente, clave
            FROM cliente_usuario
            WHERE email = ?
        """
        cursor.execute(sql, (data.email,))
        row = cursor.fetchone()

        if not row:
            logger.warning(
                f"Login fallido | email inexistente | email={data.email} | ip={ip_cliente}"
            )
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        idcliente, password_db = row

        # ⚠️ Comparación simple (pendiente hash)
        if data.password != password_db:
            logger.warning(
                f"Login fallido | password incorrecto | idcliente={idcliente} | ip={ip_cliente}"
            )
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        payload = {
            "user_id": idcliente,
            "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        logger.info(
            f"Login exitoso | idcliente={idcliente} | ip={ip_cliente}"
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in_hours": TOKEN_EXPIRE_HOURS
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            f"Error interno login | email={data.email} | ip={ip_cliente} | error={repr(e)}"
        )
        raise HTTPException(status_code=500, detail="Error interno del servidor")

    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
        except:
            pass
