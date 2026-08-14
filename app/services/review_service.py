from sqlmodel import Session, select
from app.models.review import Review, ReviewCreate


def create_review(
    session: Session,
    review_in: ReviewCreate,
    user_id: int,
    product_id: int,
) -> Review:
    review_db = Review.model_validate(
        review_in,
        update={"user_id": user_id, "product_id": product_id},
    )
    session.add(review_db)
    session.commit()
    session.refresh(review_db)
    return review_db


def get_reviews_by_product(
    session: Session,
    product_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Review]:
    statement = (
        select(Review)
        .where(Review.product_id == product_id)
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def get_review_by_id(session: Session, review_id: int) -> Review | None:
    return session.get(Review, review_id)
