from fastapi import APIRouter

from app.api.routes import (
    auth,
    tasks,
    categories,
    reviews,
    products,
    cart,
)


# =========================================================
# ROUTER PRINCIPAL DE LA API
# =========================================================

api_router = APIRouter()


# =========================================================
# AUTENTICACIÓN Y USUARIOS
# =========================================================

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth & Usuarios"],
)


# =========================================================
# TAREAS
# =========================================================

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Lista de Tareas"],
)


# =========================================================
# CATEGORÍAS
# =========================================================

api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["Categorías"],
)


# =========================================================
# PRODUCTOS
# =========================================================

api_router.include_router(
    products.router,
    prefix="/products",
    tags=["Productos"],
)


# =========================================================
# RESEÑAS DE PRODUCTOS
#
# Las rutas finales serán:
#
# GET
# /api/v1/products/{product_id}/reviews
#
# POST
# /api/v1/products/{product_id}/reviews
# =========================================================

api_router.include_router(
    reviews.router,
    prefix="/products",
    tags=["Reseñas de Productos"],
)


# =========================================================
# CARRITO DE COMPRAS
#
# Ejemplos:
#
# GET    /api/v1/cart/
# POST   /api/v1/cart/
# PATCH  /api/v1/cart/{cart_item_id}
# DELETE /api/v1/cart/{cart_item_id}
#
# Pago simulado:
# POST   /api/v1/cart/checkout
# =========================================================

api_router.include_router(
    cart.router,
    prefix="/cart",
    tags=["Carrito de Compras"],
)