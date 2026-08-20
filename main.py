from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_db_and_tables


# ============================================================
# LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando la Base de Datos...")
    create_db_and_tables()
    yield
    print("Apagando API de forma segura...")


# ============================================================
# APLICACIÓN
# ============================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Proyecto Base del Taller de Actualización",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    # Producción
    allow_origins=[
        "https://cody-apps-internet-frontend-ng.vercel.app",
    ],

    # Desarrollo local:
    # localhost:4200, 4201, 4300, etc.
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# ENDPOINT PRINCIPAL
# ============================================================

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Backend funcionando correctamente"
    }


# ============================================================
# ROUTER
# ============================================================

from app.api.main_router import api_router

app.include_router(
    api_router,
    prefix=settings.API_V1_STR
)