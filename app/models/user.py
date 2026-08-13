from sqlmodel import SQLModel, Field

# IMPORTANTE: Distinguimos entre la Tabla Base (Tabla en disco) ...
class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, min_length=3, max_length=50)
    email: str = Field(index=True, unique=True)
    is_active: bool = Field(default=True)

# ... Y el Modelo final que será verdaderamente la Tabla creada en SQLite/Postgres.
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    
    # Este campo vital JAMÁS debe viajar nativamente en los JSON de salida,
    # Por eso creamos luego los "Schemas/DTO" que ocultan esta contraseña al Front.
    hashed_password: str

# Schema: Lo que espera el cliente para Leer al usuario (Sin contraseña)
class UserPublic(UserBase):
    id: int

# Schema: Lo que envía el cliente desde su Angular al Formulario para Crear
class UserCreate(UserBase):
    password: str
