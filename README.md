# API Starter Template - Taller Internet

Un template robusto que incluye **SQLModel**, **Autenticación con JWT** y el **Patrón Repositorio / Service** construido nativamente encima de FastAPI.

## Pasos para Levantar (Desarrollo Local)

Estos pasos asumen que tienes Python instalado (preferiblemente mediante `pyenv` o nativo versión `3.10+`) y estás usando la línea de comandos de Linux/WSL.

### 1. Entorno Virtual y Dependencias
Evita la polución de paquetes en tu sistema creando un "Cuarto Limpio":

```bash
# Crear el entorno (solo se hace la primera vez)
python3 -m venv venv

# Activar el entorno (hacerlo CADA VEZ que abras una terminal nueva)
source venv/bin/activate

# Instalar los paquetes del proyecto
pip install -r requirements.txt
```

### 2. Configurar Entorno Seguro
El proyecto nunca debe subir sus claves a Git. Crearemos el archivo local para ti mismo:
Copia el archivo `.env.example` y renómbralo a `.env`.

```bash
cp .env.example .env
```

### 3. Encender el Servidor
Dado que usamos SQLite internamente, no necesitas instalar PostgreSQL en tu PC. La base de datos se creará automática (fichero `.db`) en el primer arranque.

```bash
uvicorn main:app --reload
```

## Exploración Automática (Docs)
Al encender, revisa tus rutas y prueba tu JWT (botón "Authorize" verde) abriendo en tu navegador local la URL mágica de FastAPI:

👉 <a href=\"http://localhost:8000/docs\" target=\"_blank\">http://localhost:8000/docs</a>
