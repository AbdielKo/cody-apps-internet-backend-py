from sqlmodel import Session, select
from app.models.cart_item import CartItem, CartItemCreate, CartItemUpdate


def get_cart_items(session: Session, user_id: int) -> list[CartItem]:
    """Obtiene todos los elementos del carrito de un usuario."""
    statement = select(CartItem).where(CartItem.user_id == user_id)
    return list(session.exec(statement).all())


def get_cart_item_by_id_and_user(
    session: Session, cart_item_id: int, user_id: int
) -> CartItem | None:
    """Busca un ítem específico del carrito validando la pertenencia al usuario."""
    statement = select(CartItem).where(
        CartItem.id == cart_item_id,
        CartItem.user_id == user_id,
    )
    return session.exec(statement).first()


def add_to_cart(
    session: Session,
    cart_item_in: CartItemCreate,
    user_id: int,
) -> CartItem:
    """
    Añade un producto al carrito del usuario.
    - Seguridad: user_id se inyecta por separado, nunca desde el esquema del cliente.
    - Lógica de negocio: Si el producto ya está en el carrito, suma la cantidad.
    """
    # Verificar si el producto ya existe en el carrito del usuario
    statement = select(CartItem).where(
        CartItem.user_id == user_id,
        CartItem.product_id == cart_item_in.product_id,
    )
    existing_item = session.exec(statement).first()

    if existing_item:
        existing_item.quantity += cart_item_in.quantity
        session.add(existing_item)
        session.commit()
        session.refresh(existing_item)
        return existing_item

    # Si no existe, creamos un nuevo registro asociando el user_id autenticado
    cart_item = CartItem(
        user_id=user_id,
        product_id=cart_item_in.product_id,
        quantity=cart_item_in.quantity,
    )
    session.add(cart_item)
    session.commit()
    session.refresh(cart_item)
    return cart_item


def update_cart_item(
    session: Session,
    cart_item_id: int,
    cart_item_in: CartItemUpdate,
    user_id: int,
) -> CartItem | None:
    """Actualiza la cantidad de un producto en el carrito del usuario."""
    cart_item = get_cart_item_by_id_and_user(
        session=session, cart_item_id=cart_item_id, user_id=user_id
    )
    if not cart_item:
        return None

    cart_item.quantity = cart_item_in.quantity
    session.add(cart_item)
    session.commit()
    session.refresh(cart_item)
    return cart_item


def remove_from_cart(session: Session, cart_item_id: int, user_id: int) -> bool:
    """Elimina un producto del carrito del usuario."""
    cart_item = get_cart_item_by_id_and_user(
        session=session, cart_item_id=cart_item_id, user_id=user_id
    )
    if not cart_item:
        return False

    session.delete(cart_item)
    session.commit()
    return True


def clear_cart(session: Session, user_id: int) -> None:
    """Vacía por completo el carrito del usuario."""
    items = get_cart_items(session=session, user_id=user_id)
    for item in items:
        session.delete(item)
    session.commit()
