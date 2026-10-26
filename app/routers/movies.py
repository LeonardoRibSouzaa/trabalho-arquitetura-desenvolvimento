from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.movie import Movie
from app.models.user import User
from app.schemas.movie import MovieCreate, MovieUpdate, MovieResponse, GENRES_VALIDOS
from app.auth.security import get_current_user

router = APIRouter(prefix="/movies", tags=["Filmes"])


@router.get("", response_model=list[MovieResponse])
def list_movies(
    genre: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Movie)

    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))
    if year:
        query = query.filter(Movie.year == year)

    offset = (page - 1) * limit
    return query.order_by(Movie.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filme não encontrado"
        )
    return movie


@router.post("", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie(
    movie_data: MovieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if movie_data.genre.lower() not in GENRES_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gênero inválido. Gêneros aceitos: {', '.join(GENRES_VALIDOS)}"
        )

    new_movie = Movie(
        title=movie_data.title,
        genre=movie_data.genre.lower(),
        year=movie_data.year,
        director=movie_data.director,
        synopsis=movie_data.synopsis,
        created_by=current_user.id
    )
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie


@router.put("/{movie_id}", response_model=MovieResponse)
def update_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filme não encontrado"
        )

    if movie.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para editar este filme"
        )

    if movie_data.genre.lower() not in GENRES_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gênero inválido. Gêneros aceitos: {', '.join(GENRES_VALIDOS)}"
        )

    movie.title = movie_data.title
    movie.genre = movie_data.genre.lower()
    movie.year = movie_data.year
    movie.director = movie_data.director
    movie.synopsis = movie_data.synopsis

    db.commit()
    db.refresh(movie)
    return movie


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filme não encontrado"
        )

    if movie.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para excluir este filme"
        )

    db.delete(movie)
    db.commit()
