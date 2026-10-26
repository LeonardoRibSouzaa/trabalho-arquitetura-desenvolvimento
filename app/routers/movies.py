"""
Router de Filmes.
Endpoints CRUD completo para o recurso principal da API.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.movie import Movie
from app.models.user import User
from app.schemas.movie import MovieCreate, MovieUpdate, MovieResponse, GENRES_VALIDOS
from app.auth.security import get_current_user

router = APIRouter(prefix="/movies", tags=["Filmes"])


@router.get(
    "",
    response_model=list[MovieResponse],
    summary="Listar filmes",
    description="Retorna uma lista paginada de filmes. Permite filtrar por gênero e/ou ano."
)
def list_movies(
    genre: Optional[str] = Query(None, description="Filtrar por gênero (ex: drama, ação)"),
    year: Optional[int] = Query(None, description="Filtrar por ano de lançamento"),
    page: int = Query(1, ge=1, description="Número da página (padrão: 1)"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página (padrão: 10, máx: 100)"),
    db: Session = Depends(get_db)
):
    """
    Lista todos os filmes cadastrados com suporte a paginação e filtros opcionais.

    - **genre**: Filtra filmes cujo gênero contenha o texto informado
    - **year**: Filtra filmes pelo ano exato de lançamento
    - **page**: Página desejada (começa em 1)
    - **limit**: Quantidade de resultados por página
    """
    query = db.query(Movie)

    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))
    if year:
        query = query.filter(Movie.year == year)

    offset = (page - 1) * limit
    movies = query.order_by(Movie.created_at.desc()).offset(offset).limit(limit).all()
    return movies


@router.get(
    "/{movie_id}",
    response_model=MovieResponse,
    summary="Consultar filme por ID",
    description="Retorna os dados de um filme específico pelo seu identificador."
)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    Busca um filme pelo ID.

    - **movie_id**: Identificador único do filme

    Retorna 404 se o filme não for encontrado.
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filme não encontrado"
        )
    return movie


@router.post(
    "",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo filme",
    description="Cadastra um novo filme no catálogo. Requer autenticação JWT."
)
def create_movie(
    movie_data: MovieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo filme vinculado ao usuário autenticado.

    - **title**: Título do filme (obrigatório)
    - **genre**: Gênero válido (obrigatório)
    - **year**: Ano de lançamento (obrigatório, entre 1888 e 2026)
    - **director**: Nome do diretor (obrigatório)
    - **synopsis**: Sinopse do filme (opcional)

    🔒 Endpoint protegido — requer token JWT no header Authorization.
    """
    # Validação do gênero contra lista de valores aceitos
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


@router.put(
    "/{movie_id}",
    response_model=MovieResponse,
    summary="Atualizar filme",
    description="Atualiza todos os campos de um filme existente. Requer autenticação JWT e ser o criador do filme."
)
def update_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um filme existente (substituição completa — PUT).

    Somente o usuário que cadastrou o filme pode atualizá-lo.

    🔒 Endpoint protegido — requer token JWT no header Authorization.
    """
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filme não encontrado"
        )

    # Verifica se o usuário autenticado é o criador do filme
    if movie.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para editar este filme"
        )

    # Validação do gênero
    if movie_data.genre.lower() not in GENRES_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gênero inválido. Gêneros aceitos: {', '.join(GENRES_VALIDOS)}"
        )

    # Atualiza todos os campos (PUT = substituição completa)
    movie.title = movie_data.title
    movie.genre = movie_data.genre.lower()
    movie.year = movie_data.year
    movie.director = movie_data.director
    movie.synopsis = movie_data.synopsis

    db.commit()
    db.refresh(movie)
    return movie


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir filme",
    description="Remove um filme do catálogo. Requer autenticação JWT e ser o criador do filme."
)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Exclui um filme e todas as suas avaliações associadas.

    Somente o usuário que cadastrou o filme pode excluí-lo.

    🔒 Endpoint protegido — requer token JWT no header Authorization.
    """
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
