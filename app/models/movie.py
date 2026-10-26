"""
Modelo ORM do Filme.
Mapeia a tabela 'movies' no banco de dados.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Movie(Base):
    """
    Representa um filme no catálogo.
    Cada filme pertence a um usuário (quem cadastrou) e pode ter várias avaliações.
    """
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    genre = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    director = Column(String(100), nullable=False)
    synopsis = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    creator = relationship("User", back_populates="movies")
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")
