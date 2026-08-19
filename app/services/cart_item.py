from sqlmodel import Session, select

from app.models.cart_item import (
    CartItem,
    CartItemCreate,
    CartItemUpdate,
)

from app.models.product import Product


# =========================================================
# OBTENER TODOS LOS ITEMS DEL CARRITO DE UN USUARIO
# =========================================================

def get_cart_items(
    session: Session,
    user_id: int,
) -> list[CartItem]:

    statement = select(CartItem).where(
        CartItem.user_id == user_id
    )

    return list(
        session.exec(statement).all()
    )


# =========================================================
# BUSCAR ITEM POR ID + USUARIO
# =========================================================

def get_cart_item_by_id_and_user(
    session: Session,
    cart_item_id: int,
    user_id: int,
) -> CartItem | None:

    statement = select(CartItem).where(
        CartItem.id == cart_item_id,
        CartItem.user_id == user_id,
    )

    return session.exec(statement).first()


# =========================================================
# BUSCAR ITEM POR PRODUCTO + USUARIO
# =========================================================

def get_cart_item_by_product_and_user(
    session: Session,
    product_id: int,
    user_id: int,
) -> CartItem | None:

    statement = select(CartItem).where(
        CartItem.product_id == product_id,
        CartItem.user_id == user_id,
    )

    return session.exec(statement).first()


# =========================================================
# AGREGAR PRODUCTO AL CARRITO
# =========================================================

def add_to_cart(
    session: Session,
    cart_item_in: CartItemCreate,
    user_id: int,
) -> CartItem:

    # Verificar si ya existe ese producto en el carrito
    existing_item = get_cart_item_by_product_and_user(
        session=session,
        product_id=cart_item_in.product_id,
        user_id=user_id,
    )

    # Si ya existe, sumamos cantidad
    if existing_item:

        existing_item.quantity += cart_item_in.quantity

        session.add(existing_item)

        session.commit()

        session.refresh(existing_item)

        return existing_item


    # Si no existe, creamos un nuevo item
    cart_item = CartItem(
        user_id=user_id,
        product_id=cart_item_in.product_id,
        quantity=cart_item_in.quantity,
    )

    session.add(cart_item)

    session.commit()

    session.refresh(cart_item)

    return cart_item


# =========================================================
# ACTUALIZAR CANTIDAD
# =========================================================

def update_cart_item(
    session: Session,
    cart_item_id: int,
    cart_item_in: CartItemUpdate,
    user_id: int,
) -> CartItem | None:

    cart_item = get_cart_item_by_id_and_user(
        session=session,
        cart_item_id=cart_item_id,
        user_id=user_id,
    )

    if not cart_item:
        return None

    cart_item.quantity = cart_item_in.quantity

    session.add(cart_item)

    session.commit()

    session.refresh(cart_item)

    return cart_item


# =========================================================
# ELIMINAR UN PRODUCTO DEL CARRITO
# =========================================================

def remove_from_cart(
    session: Session,
    cart_item_id: int,
    user_id: int,
) -> bool:

    cart_item = get_cart_item_by_id_and_user(
        session=session,
        cart_item_id=cart_item_id,
        user_id=user_id,
    )

    if not cart_item:
        return False

    session.delete(cart_item)

    session.commit()

    return True


# =========================================================
# VACIAR CARRITO
# =========================================================

def clear_cart(
    session: Session,
    user_id: int,
) -> None:

    items = get_cart_items(
        session=session,
        user_id=user_id,
    )

    for item in items:
        session.delete(item)

    session.commit()


# =========================================================
# CHECKOUT / PAGO SIMULADO
# =========================================================

def checkout_cart(
    session: Session,
    user_id: int,
) -> dict:

    # Obtener carrito completo
    items = get_cart_items(
        session=session,
        user_id=user_id,
    )

    if not items:
        raise ValueError(
            "El carrito está vacío"
        )


    # -----------------------------------------------------
    # PRIMERO VALIDAMOS TODOS LOS PRODUCTOS
    # ANTES DE MODIFICAR LA BASE DE DATOS
    # -----------------------------------------------------

    validated_items: list[
        tuple[CartItem, Product]
    ] = []

    total = 0.0


    for item in items:

        product = session.get(
            Product,
            item.product_id,
        )


        if not product:

            raise ValueError(
                f"El producto con ID "
                f"{item.product_id} ya no existe"
            )


        # Verificar cantidad válida
        if item.quantity <= 0:

            raise ValueError(
                f"La cantidad de "
                f"{product.title} no es válida"
            )


        # VERIFICACIÓN IMPORTANTE DE STOCK
        if item.quantity > product.stock:

            raise ValueError(
                f"Stock insuficiente para "
                f"{product.title}. "
                f"Disponible: {product.stock}. "
                f"Solicitado: {item.quantity}."
            )


        total += (
            float(product.price)
            * item.quantity
        )


        validated_items.append(
            (item, product)
        )


    # -----------------------------------------------------
    # TODO ES VÁLIDO:
    # AHORA DESCONTAMOS EL STOCK
    # -----------------------------------------------------

    for item, product in validated_items:

        product.stock -= item.quantity

        session.add(product)


    # -----------------------------------------------------
    # VACIAR CARRITO DESPUÉS DE LA COMPRA
    # -----------------------------------------------------

    for item, _product in validated_items:

        session.delete(item)


    # Guardamos TODO junto
    session.commit()


    return {
        "message": (
            "Pago simulado realizado correctamente"
        ),
        "total": round(total, 2),
    }