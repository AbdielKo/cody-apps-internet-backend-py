from fastapi import APIRouter
from app.api.routes import auth, tasks

# Este es el router base. 
# Si agregamos entidades en el futuro (Productos, Categorias), solo los registramos aquí con 2 lineas de código.

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth & Usuarios"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Lista de Tareas (CRUD simple)"])
