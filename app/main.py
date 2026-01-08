from fastapi import FastAPI
from app.routers.envio_router import router as envio_router
from app.routers.auth_router import router as auth_router

app = FastAPI(
    title="API de Envíos",
    description="API para recibir mensajes y registrarlos",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(envio_router)