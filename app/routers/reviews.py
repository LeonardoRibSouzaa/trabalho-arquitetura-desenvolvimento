"""
Router de Avaliações.
Endpoints para listar e criar avaliações de filmes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.movie import Movie
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse
from app.auth.security import get_current_user

router = APIRouter(prefix="/movies/{movie_id}/reviews", tags=["Avaliações"])


@router.get(
    "",
    response_model=list[ReviewResponse],
    summary="Listar avaliações de um filme",
    description="Retorna todas as avaliações de um filme específico."
)
def list_reviews(movie_id: int, db: Session = Depends(get_db)):
    """
    Lista todas as avaliações de um filme.

    - **movie_id**: Identificador do filme

    Retorna 404 se o filme não existir.
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filme não encontrado"
        )

    reviews = db.query(Review).filter(Review.movie_id == movie_id).all()
    return reviews


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar avaliação para um filme",
    description="Adiciona uma avaliação a um filme. Cada usuário pode avaliar um filme apenas uma vez. Requer autenticação JWT."
)
def create_review(
    movie_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria uma nova avaliação para um filme.

    - **rating**: Nota de 1.0 a 10.0 (obrigatório)
    - **comment**: Comentário ou resenha (opcional, máx 1000 caracteres)

    Regras:
    - O filme deve existir
    - O usuário só pode avaliar cada filme uma vez

    🔒 Endpoint protegido — requer token JWT no header Authorization.
    """
    # Verifica se o filme existe
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filme não encontrado"
        )

    # Verifica se o usuário já avaliou este filme
    existing_review = db.query(Review).filter(
        Review.movie_id == movie_id,
        Review.user_id == current_user.id
    ).first()
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Você já avaliou este filme"
        )

    new_review = Review(
        movie_id=movie_id,
        user_id=current_user.id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review
