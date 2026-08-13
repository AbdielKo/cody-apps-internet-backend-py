from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.models.user import User
from app.services import user_service

# OAuth2 requerirá que el frontend envíe sus JSON Web Tokens usando autorización HTTP tipo Bearer
# tokenUrl indica a Swagger Docs a qué endpoint interno disparar para loguearse visualmente.
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Alias de tipado moderno de Python 3.9+ (Para que las rutas queden limpísimas)
SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

# ==========================================================
# GUARDIA DE SEGURIDAD GLOBAL: get_current_user
# ==========================================================
def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """
    Función Dependencia.
    Al escribir `usuario_actual = Depends(get_current_user)` en una ruta:
    1. FastAPI frena el request.
    2. Lee el token de la cabecera.
    3. Lo evalua matemáticamente usando el Secret de tu .env.
    4. Si falla, bota Error 401. Si es válido, busca al usuario en SQLite.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales invalidas o token expirado. Vuelve a iniciar sesión.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Desencriptar el Token JWT
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Extraer de SQLite el usuario que dice ser
    user = user_service.get_user_by_id(session=session, user_id=int(user_id_str))
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado en BD")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo/baneado")
        
    return user

# Creamos otro alias para forzar el Logueo en 1 sola línea en Controladores
CurrentUser = Annotated[User, Depends(get_current_user)]
