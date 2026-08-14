from typing import Optional
from sqlmodel import Field, SQLModel


# Esquema Base con campos compartidos
class ReviewBase(SQLModel):
    rating: int = Field(ge=1, le=5, description="Calificación de 1 a 5 estrellas")
    comment: Optional[str] = Field(default=None)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")


# Modelo de Base de Datos
class Review(ReviewBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Esquema para Creación (POST)
class ReviewCreate(ReviewBase):
    pass


# Esquema Público para Lectura (GET)
class ReviewPublic(ReviewBase):
    id: int
