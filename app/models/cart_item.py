from typing import Optional
from sqlmodel import Field, SQLModel


# Esquema Base con campos compartidos
class CartItemBase(SQLModel):
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(default=1, ge=1, description="Cantidad del producto")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")


# Modelo de Base de Datos
class CartItem(CartItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


# Esquema para Creación (POST)
class CartItemCreate(SQLModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


# Esquema para Actualización de Cantidad (PATCH/PUT)
class CartItemUpdate(SQLModel):
    quantity: int = Field(ge=1)


# Esquema Público para Lectura (GET)
class CartItemPublic(CartItemBase):
    id: int
    user_id: int
