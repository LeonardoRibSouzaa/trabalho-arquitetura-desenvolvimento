"""
Schemas Pydantic para validação de dados de Filme.
Define os formatos de entrada e saída das requisições de filmes.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Lista de gêneros válidos aceitos pela API
GENRES_VALIDOS = [
    "ação", "aventura", "comédia", "drama", "terror",
    "ficção científica", "romance", "suspense", "animação",
    "documentário", "fantasia", "musical", "guerra", "western", "outro"
]


class MovieCreate(BaseModel):
    """Schema para criação de novo filme."""
    title: str = Field(
        ..., min_length=1, max_length=200,
        description="Título do filme",
        examples=["O Poderoso Chefão"]
    )
    genre: str = Field(
        ..., description=f"Gênero do filme. Valores aceitos: {', '.join(GENRES_VALIDOS)}",
        examples=["drama"]
    )
    year: int = Field(
        ..., ge=1888, le=2026,
        description="Ano de lançamento (entre 1888 e 2026)",
        examples=[1972]
    )
    director: str = Field(
        ..., min_length=1, max_length=100,
        description="Nome do diretor",
        examples=["Francis Ford Coppola"]
    )
    synopsis: Optional[str] = Field(
        None, max_length=2000,
        description="Sinopse do filme (opcional)",
        examples=["A história da família Corleone e do submundo da máfia."]
    )


class MovieUpdate(BaseModel):
    """
    Schema para atualização completa de um filme (PUT).
    Todos os campos obrigatórios devem ser enviados.
    """
    title: str = Field(..., min_length=1, max_length=200, description="Título do filme")
    genre: str = Field(..., description="Gênero do filme")
    year: int = Field(..., ge=1888, le=2026, description="Ano de lançamento")
    director: str = Field(..., min_length=1, max_length=100, description="Nome do diretor")
    synopsis: Optional[str] = Field(None, max_length=2000, description="Sinopse do filme")


class MovieResponse(BaseModel):
    """Schema de resposta com dados completos do filme."""
    id: int
    title: str
    genre: str
    year: int
    director: str
    synopsis: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
