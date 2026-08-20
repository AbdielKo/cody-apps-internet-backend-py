from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import SessionDep, CurrentUser
from app.models.task import TaskCreate, TaskPublic, TaskUpdate
from app.services import task_service


router = APIRouter()


# ============================================================
# MODELO DE ENTRADA PARA IA
# ============================================================

class PromptRequest(BaseModel):

    prompt: str = Field(
        min_length=3,
        max_length=1000
    )


# ============================================================
# MODELO DE RESPUESTA DE LA IA
# ============================================================

class TaskSuggestion(BaseModel):

    title: str

    description: str


# ============================================================
# LISTAR TAREAS
# ============================================================

@router.get(
    "/",
    response_model=list[TaskPublic]
)
def leer_tareas(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100
) -> Any:

    return task_service.get_tasks(
        session=session,
        skip=skip,
        limit=limit
    )


# ============================================================
# CREAR TAREA NORMAL
# ============================================================

@router.post(
    "/",
    response_model=TaskPublic
)
def crear_tarea(
    session: SessionDep,
    current_user: CurrentUser,
    task_in: TaskCreate
) -> Any:

    return task_service.create_task(
        session=session,
        task_in=task_in
    )


# ============================================================
# GENERAR SUGERENCIA CON IA
#
# NO GUARDA NADA EN LA BASE DE DATOS.
# ============================================================

@router.post(
    "/ai-suggest",
    response_model=TaskSuggestion
)
def sugerir_tarea_con_ia(
    request: PromptRequest,
    current_user: CurrentUser
) -> TaskSuggestion:

    try:

        result = task_service.suggest_task_ai(
            prompt=request.prompt
        )


        return TaskSuggestion(
            title=result["title"],
            description=result["description"]
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


    except Exception as error:

        print(
            f"Error comunicándose con Z.AI: {error}"
        )

        raise HTTPException(
            status_code=502,
            detail="No se pudo obtener la sugerencia de la IA"
        ) from error


# ============================================================
# ACTUALIZAR TAREA
# ============================================================

@router.patch(
    "/{task_id}",
    response_model=TaskPublic
)
def actualizar_tarea(
    session: SessionDep,
    current_user: CurrentUser,
    task_id: int,
    task_in: TaskUpdate
) -> Any:

    task_db = task_service.update_task(
        session=session,
        task_id=task_id,
        task_in=task_in
    )

    if not task_db:

        raise HTTPException(
            status_code=404,
            detail="Tarea no encontrada ❌"
        )

    return task_db


# ============================================================
# ELIMINAR TAREA
# ============================================================

@router.delete(
    "/{task_id}"
)
def borrar_tarea(
    session: SessionDep,
    current_user: CurrentUser,
    task_id: int
) -> dict:

    deleted = task_service.delete_task(
        session=session,
        task_id=task_id
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Tarea no encontrada ❌"
        )


    return {
        "mensaje":
            f"Tarea {task_id} borrada exitosamente de la base de datos"
    }