# 🚀 FastAPI Template - Taller de Aplicaciones de Internet

<div align="center">
  <i>Repositorio Base Oficial para el Módulo de Backend (Python & FastAPI).</i><br>
  <b><a href="https://cody-apps-internet.vercel.app/" target="_blank">🌐 Ver el Curso y Materiales de Estudio Completos</a></b>
</div>

---

## 📖 Acerca de este Proyecto

Este repositorio es una plantilla fundacional (Boilerplate) diseñada con rigor arquitectónico. Implementa los principios de **Clean Architecture** (Arquitectura de Capas: `Routers -> Services -> Models`), **Inyección de Dependencias** y **Seguridad Robusta**, construida nativamente encima de [FastAPI](https://fastapi.tiangolo.com/).

### Tecnologías Principales:
* **Framework:** FastAPI
* **ORM & Validación:** SQLModel + Pydantic
* **Seguridad:** JWT (JSON Web Tokens) + Hashing de Contraseñas (Passlib/Bcrypt)
* **Base de Datos:** SQLite (Configurado por defecto, listo para migrar a PostgreSQL)

---

## ⚙️ Guía de Arranque Rápido (Desarrollo Local)

Sigue estos pasos cuidadosamente para levantar la API en tu entorno local. 
> ⚠️ **Requisito Mínimo:** Asegúrate de tener instalado **Python 3.9 o superior**.

### 1. Entorno Virtual y Dependencias

Aísla las dependencias del proyecto creando un entorno virtual ("Cuarto Limpio") para evitar conflictos en tu sistema:

```bash
# 1. Crear el entorno virtual (solo la primera vez)
python3 -m venv venv

# 2. Activar el entorno virtual (haz esto SIEMPRE que abras una nueva terminal)
source venv/bin/activate  # En Linux/macOS/WSL

# 3. Instalar dependencias estrictas
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno y Seguridad

Por seguridad, las claves maestras y configuraciones jamás se suben al código fuente. 

```bash
# 1. Copiar la plantilla de configuración
cp .env.example .env
```

**Generación de Clave Criptográfica:**
Abre el archivo `.env` recién creado. Necesitas reemplazar el valor de `SECRET_KEY`. **Nunca uses una contraseña fácil (ej. 123456).** Genera un hash criptográfico de 32 bytes ejecutando este comando en tu terminal, y pega el resultado en tu archivo `.env`:

```bash
openssl rand -hex 32
```

### 3. Encender el Servidor

Gracias a SQLModel y SQLite, la base de datos se autoconstruirá (archivo `taller_db.db`) en el primer encendido. Para levantar el servidor en modo desarrollo (recarga automática):

```bash
# Enciende Uvicorn apuntando al archivo main.py (en la raíz)
uvicorn main:app --reload
```

---

## 🧪 Exploración y Pruebas (Swagger UI)

Una vez que el servidor indique que ha arrancado exitosamente, FastAPI autogenerará una documentación interactiva completa con OpenAPI.

Abre tu navegador y visita:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

Desde esta interfaz podrás:
1. Registrar un nuevo usuario.
2. Autenticarte (usando el candado verde "Authorize") para inyectar tu JWT.
3. Probar los endpoints CRUD base que vienen pre-construidos en este repositorio.

¡Feliz codificación! 🧑‍💻👩‍💻
