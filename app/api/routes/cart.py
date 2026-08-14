from typing import Any
from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models.cart_item import CartItemCreate, CartItemPublic, CartItemUpdate
from app.services import cart_item as cart_service, product_service

router = APIRouter()


@router.get("/", response_model=list[CartItemPublic])
def read_cart_items(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Obtiene todos los productos del carrito del usuario autenticado."""
    return cart_service.get_cart_items(session=session, user_id=current_user.id)


@router.post("/", response_model=CartItemPublic)
def add_product_to_cart(
    cart_item_in: CartItemCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Añade un producto al carrito personal del usuario.
    - Seguridad: user_id se extrae del token JWT (current_user.id).
    - Prohibido recibir user_id en el payload del cliente.
    """
    # 1. Validar que el producto a añadir exista
    product = product_service.get_product_by_id(
        session=session, product_id=cart_item_in.product_id
    )
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # 2. Guardar en el carrito del usuario
    return cart_service.add_to_cart(
        session=session,
        cart_item_in=cart_item_in,
        user_id=current_user.id,
    )


@router.patch("/{cart_item_id}", response_model=CartItemPublic)
def update_cart_item_quantity(
    cart_item_id: int,
    cart_item_in: CartItemUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Actualiza la cantidad de un ítem en el carrito del usuario."""
    cart_item = cart_service.update_cart_item(
        session=session,
        cart_item_id=cart_item_id,
        cart_item_in=cart_item_in,
        user_id=current_user.id,
    )
    if not cart_item:
        raise HTTPException(
            status_code=404, detail="Elemento no encontrado en tu carrito"
        )
    return cart_item


@router.delete("/{cart_item_id}")
def remove_item_from_cart(
    cart_item_id: int,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """Elimina un ítem específico del carrito del usuario."""
    deleted = cart_service.remove_from_cart(
        session=session,
        cart_item_id=cart_item_id,
        user_id=current_user.id,
    )
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Elemento no encontrado en tu carrito"
        )
    return {"message": "Producto eliminado del carrito exitosamente"}


@router.delete("/")
def empty_cart(
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """Vacía por completo el carrito del usuario autenticado."""
    cart_service.clear_cart(session=session, user_id=current_user.id)
    return {"message": "Carrito vaciado exitosamente"}
