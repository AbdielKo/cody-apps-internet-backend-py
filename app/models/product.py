from typing import Optional
from sqlmodel import Field, SQLModel


# Esquema Base con campos compartidos
class ProductBase(SQLModel):
    title: str = Field(index=True, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")


# Modelo de Base de Datos
class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Esquema para Creación (POST)
class ProductCreate(ProductBase):
    pass


# Esquema Público para Lectura (GET)
class ProductPublic(ProductBase):
    id: int


# Esquema para Actualización Parcial (PATCH/PUT)
class ProductUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
