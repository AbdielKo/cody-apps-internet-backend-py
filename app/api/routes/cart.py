from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep

from app.models.cart_item import (
    CartItemCreate,
    CartItemPublic,
    CartItemUpdate,
)

from app.services import (
    cart_item as cart_service,
    product_service,
)


router = APIRouter()


# =========================================================
# GET - OBTENER CARRITO
# =========================================================

@router.get(
    "/",
    response_model=list[CartItemPublic],
)
def read_cart_items(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:

    return cart_service.get_cart_items(
        session=session,
        user_id=current_user.id,
    )


# =========================================================
# POST - AGREGAR PRODUCTO AL CARRITO
# =========================================================

@router.post(
    "/",
    response_model=CartItemPublic,
)
def add_product_to_cart(
    cart_item_in: CartItemCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:

    # -----------------------------------------------------
    # 1. VERIFICAR QUE EL PRODUCTO EXISTA
    # -----------------------------------------------------

    product = product_service.get_product_by_id(
        session=session,
        product_id=cart_item_in.product_id,
    )


    if not product:

        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )


    # -----------------------------------------------------
    # 2. VERIFICAR QUE TENGA STOCK
    # -----------------------------------------------------

    if product.stock <= 0:

        raise HTTPException(
            status_code=400,
            detail=(
                f'El producto "{product.title}" '
                f'está agotado.'
            ),
        )


    # -----------------------------------------------------
    # 3. VER CUÁNTAS UNIDADES YA HAY EN CARRITO
    # -----------------------------------------------------

    existing_item = (
        cart_service
        .get_cart_item_by_product_and_user(
            session=session,
            product_id=cart_item_in.product_id,
            user_id=current_user.id,
        )
    )


    current_quantity = (
        existing_item.quantity
        if existing_item
        else 0
    )


    requested_total = (
        current_quantity
        + cart_item_in.quantity
    )


    # -----------------------------------------------------
    # 4. NO PERMITIR SUPERAR STOCK
    # -----------------------------------------------------

    if requested_total > product.stock:

        available_to_add = max(
            0,
            product.stock - current_quantity,
        )


        raise HTTPException(
            status_code=400,
            detail=(
                f'Stock insuficiente para '
                f'"{product.title}". '
                f'Stock total: {product.stock}. '
                f'Ya tienes en carrito: '
                f'{current_quantity}. '
                f'Puedes agregar como máximo: '
                f'{available_to_add}.'
            ),
        )


    # -----------------------------------------------------
    # 5. AGREGAR
    # -----------------------------------------------------

    return cart_service.add_to_cart(
        session=session,
        cart_item_in=cart_item_in,
        user_id=current_user.id,
    )


# =========================================================
# POST - PAGO SIMULADO / CHECKOUT
# =========================================================

@router.post("/checkout")
def checkout(
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:

    try:

        return cart_service.checkout_cart(
            session=session,
            user_id=current_user.id,
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


# =========================================================
# PATCH - MODIFICAR CANTIDAD
# =========================================================

@router.patch(
    "/{cart_item_id}",
    response_model=CartItemPublic,
)
def update_cart_item_quantity(
    cart_item_id: int,
    cart_item_in: CartItemUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:

    # -----------------------------------------------------
    # 1. BUSCAR ITEM
    # -----------------------------------------------------

    cart_item = (
        cart_service
        .get_cart_item_by_id_and_user(
            session=session,
            cart_item_id=cart_item_id,
            user_id=current_user.id,
        )
    )


    if not cart_item:

        raise HTTPException(
            status_code=404,
            detail=(
                "Elemento no encontrado "
                "en tu carrito"
            ),
        )


    # -----------------------------------------------------
    # 2. BUSCAR PRODUCTO
    # -----------------------------------------------------

    product = product_service.get_product_by_id(
        session=session,
        product_id=cart_item.product_id,
    )


    if not product:

        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )


    # -----------------------------------------------------
    # 3. VALIDAR STOCK
    # -----------------------------------------------------

    if cart_item_in.quantity > product.stock:

        raise HTTPException(
            status_code=400,
            detail=(
                f'Stock insuficiente para '
                f'"{product.title}". '
                f'Solo existen '
                f'{product.stock} unidades.'
            ),
        )


    # -----------------------------------------------------
    # 4. ACTUALIZAR
    # -----------------------------------------------------

    updated_item = (
        cart_service.update_cart_item(
            session=session,
            cart_item_id=cart_item_id,
            cart_item_in=cart_item_in,
            user_id=current_user.id,
        )
    )


    if not updated_item:

        raise HTTPException(
            status_code=404,
            detail=(
                "Elemento no encontrado "
                "en tu carrito"
            ),
        )


    return updated_item


# =========================================================
# DELETE - ELIMINAR PRODUCTO DEL CARRITO
# =========================================================

@router.delete("/{cart_item_id}")
def remove_item_from_cart(
    cart_item_id: int,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:

    deleted = cart_service.remove_from_cart(
        session=session,
        cart_item_id=cart_item_id,
        user_id=current_user.id,
    )


    if not deleted:

        raise HTTPException(
            status_code=404,
            detail=(
                "Elemento no encontrado "
                "en tu carrito"
            ),
        )


    return {
        "message": (
            "Producto eliminado del carrito "
            "exitosamente"
        )
    }


# =========================================================
# DELETE - VACIAR CARRITO
# =========================================================

@router.delete("/")
def empty_cart(
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:

    cart_service.clear_cart(
        session=session,
        user_id=current_user.id,
    )


    return {
        "message": (
            "Carrito vaciado exitosamente"
        )
    }