from typing import Any
from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models.review import ReviewCreate, ReviewPublic
from app.services import product_service, review_service

router = APIRouter()


@router.post("/{product_id}/reviews", response_model=ReviewPublic)
def create_review_for_product(
    product_id: int,
    review_in: ReviewCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    # 1. Validar que el producto exista antes de asociarle una reseña
    product = product_service.get_product_by_id(session=session, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # 2. Inyección segura de user_id extraído del token JWT (current_user.id)
    return review_service.create_review(
        session=session,
        review_in=review_in,
        user_id=current_user.id,
        product_id=product_id,
    )


@router.get("/{product_id}/reviews", response_model=list[ReviewPublic])
def read_reviews_for_product(
    product_id: int,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    # Validar existencia del producto
    product = product_service.get_product_by_id(session=session, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return review_service.get_reviews_by_product(
        session=session,
        product_id=product_id,
        skip=skip,
        limit=limit,
    )
