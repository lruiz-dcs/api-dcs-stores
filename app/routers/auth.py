from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.database import get_connection
import jwt
import datetime

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = "TU_LLAVE_SECRETA_CAMBIALA"

class LoginUser(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(data: LoginUser):

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT idusuario FROM cliente_usuario
        WHERE email = ? AND clave = ?
    """

    cursor.execute(sql, (data.email, data.password))
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Crear token
    payload = {
        "user_id": row[0],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=5)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return {
        "status": "ok",
        "token": token
    }
