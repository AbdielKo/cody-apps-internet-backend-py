import json
import time

from sqlmodel import Session, select
from openai import OpenAI, RateLimitError

from app.models.task import Task, TaskCreate, TaskUpdate
from app.core.config import settings


# ============================================================
# SERVICIO DE TAREAS
# ============================================================
# Esta capa contiene la lógica de negocio.
# No conoce Request, Response ni FastAPI.
# ============================================================


# ============================================================
# LISTAR TAREAS
# ============================================================

def get_tasks(
    session: Session,
    skip: int = 0,
    limit: int = 100
) -> list[Task]:

    statement = (
        select(Task)
        .offset(skip)
        .limit(limit)
    )

    return list(
        session.exec(statement).all()
    )


# ============================================================
# OBTENER TAREA POR ID
# ============================================================

def get_task_by_id(
    session: Session,
    task_id: int
) -> Task | None:

    return session.get(
        Task,
        task_id
    )


# ============================================================
# CREAR TAREA NORMAL
# ============================================================

def create_task(
    session: Session,
    task_in: TaskCreate
) -> Task:

    task_db = Task.model_validate(
        task_in
    )

    session.add(task_db)

    session.commit()

    session.refresh(task_db)

    return task_db


# ============================================================
# GENERAR SUGERENCIA DE TAREA CON Z.AI
# ============================================================
#
# IMPORTANTE:
# ESTA FUNCIÓN NO GUARDA NADA EN LA BASE DE DATOS.
#
# ÚNICAMENTE DEVUELVE:
#
# {
#     "title": "...",
#     "description": "..."
# }
#
# Angular permitirá que el usuario revise la sugerencia
# antes de guardar la tarea.
# ============================================================

def suggest_task_ai(
    prompt: str
) -> dict[str, str]:

    # ========================================================
    # VALIDAR API KEY
    # ========================================================

    if not settings.ZHIPU_API_KEY:

        raise ValueError(
            "ZHIPU_API_KEY no está configurada"
        )


    # ========================================================
    # CREAR CLIENTE PARA Z.AI
    # ========================================================
    #
    # Usamos la librería OpenAI porque Z.AI es compatible
    # con su formato de API.
    #
    # max_retries=0:
    # Desactivamos los reintentos internos porque nosotros
    # controlaremos los reintentos manualmente.
    # ========================================================

    client = OpenAI(
        api_key=settings.ZHIPU_API_KEY,
        base_url="https://api.z.ai/api/paas/v4/",
        max_retries=0,
        timeout=30.0
    )


    # ========================================================
    # SYSTEM PROMPT
    # ========================================================

    system_prompt = """
Eres un asistente de productividad.

El usuario te dará una frase en lenguaje natural
sobre algo que necesita realizar.

Tu trabajo es extraer:

1. "title":
   Un título corto, claro y conciso.

2. "description":
   Una descripción más detallada de la tarea.

Debes conservar cualquier información importante
proporcionada por el usuario, por ejemplo:

- fecha
- hora
- lugar
- contexto
- frecuencia
- condiciones relevantes

Debes responder EXCLUSIVAMENTE en formato JSON válido.

La estructura debe ser exactamente:

{
  "title": "string",
  "description": "string"
}

No utilices Markdown.
No agregues explicaciones.
No escribas texto antes del JSON.
No escribas texto después del JSON.
"""


    # ========================================================
    # LLAMAR A Z.AI
    # ========================================================
    #
    # Z.AI puede responder ocasionalmente:
    #
    # 429
    # code 1305
    #
    # "The service may be temporarily overloaded"
    #
    # Por eso hacemos hasta 3 intentos.
    # ========================================================

    response = None

    max_attempts = 3


    for attempt in range(max_attempts):

        try:

            response = client.chat.completions.create(

                model="glm-4.5-flash",

                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.3,

                response_format={
                    "type": "json_object"
                }

            )


            # Si llegamos aquí significa que Z.AI respondió.
            break


        # ====================================================
        # Z.AI SATURADO / RATE LIMIT
        # ====================================================

        except RateLimitError as error:

            # Si ya llegamos al último intento
            if attempt == max_attempts - 1:

                raise RuntimeError(
                    "Z.AI está temporalmente saturado. "
                    "Intenta nuevamente en unos segundos."
                ) from error


            # Exponential backoff:
            #
            # Primer error:
            # 1 segundo
            #
            # Segundo error:
            # 2 segundos

            wait_seconds = 2 ** attempt


            print(
                f"Z.AI temporalmente saturado. "
                f"Reintentando en "
                f"{wait_seconds} segundo(s)..."
            )


            time.sleep(
                wait_seconds
            )


    # ========================================================
    # VALIDAR QUE EXISTA RESPUESTA
    # ========================================================

    if response is None:

        raise RuntimeError(
            "No se pudo obtener una respuesta de Z.AI"
        )


    # ========================================================
    # EXTRAER CONTENIDO DE LA RESPUESTA
    # ========================================================

    content = (
        response
        .choices[0]
        .message
        .content
    )


    if not content:

        raise ValueError(
            "La IA devolvió una respuesta vacía"
        )


    # ========================================================
    # CONVERTIR EL JSON DE LA IA A DICCIONARIO PYTHON
    # ========================================================

    try:

        ai_result = json.loads(
            content
        )


    except json.JSONDecodeError as error:

        print(
            "Respuesta inválida recibida de Z.AI:",
            content
        )

        raise ValueError(
            "La IA devolvió un JSON inválido"
        ) from error


    # ========================================================
    # EXTRAER TÍTULO
    # ========================================================

    title = str(
        ai_result.get(
            "title",
            ""
        )
    ).strip()


    # ========================================================
    # EXTRAER DESCRIPCIÓN
    # ========================================================

    description = str(
        ai_result.get(
            "description",
            ""
        )
    ).strip()


    # ========================================================
    # VALIDAR TÍTULO
    # ========================================================

    if not title:

        raise ValueError(
            "La IA no generó un título"
        )


    # ========================================================
    # DEVOLVER SUGERENCIA
    # ========================================================
    #
    # IMPORTANTE:
    # Aquí NO hacemos session.add()
    # Aquí NO hacemos session.commit()
    #
    # Por tanto, todavía NO se guarda en Neon/SQLite.
    # ========================================================

    return {
        "title": title,
        "description": description
    }


# ============================================================
# ACTUALIZAR TAREA
# ============================================================

def update_task(
    session: Session,
    task_id: int,
    task_in: TaskUpdate
) -> Task | None:

    task_db = get_task_by_id(
        session=session,
        task_id=task_id
    )


    if not task_db:

        return None


    # Solo actualiza los campos que realmente llegaron
    # desde el frontend.

    update_data = (
        task_in.model_dump(
            exclude_unset=True
        )
    )


    task_db.sqlmodel_update(
        update_data
    )


    session.add(
        task_db
    )


    session.commit()


    session.refresh(
        task_db
    )


    return task_db


# ============================================================
# ELIMINAR TAREA
# ============================================================

def delete_task(
    session: Session,
    task_id: int
) -> bool:

    task_db = get_task_by_id(
        session=session,
        task_id=task_id
    )


    if not task_db:

        return False


    session.delete(
        task_db
    )


    session.commit()


    return True