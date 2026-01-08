from typing import Optional
from pydantic import BaseModel, validator

class Envio(BaseModel):
    fechaenvio: str
    idtipo: Optional[int] = None
    urlaudio: str
    texto: str
    tipotelefono: str
    prefijo: str
    telefono: str
    nombre: str
    campo1: str
    campo2: str
    campo3: str
    campo4: str
    campo5: str
    fechahoraenvio: Optional[str] = None
    fechaencola: Optional[str] = None


