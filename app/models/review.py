"""
Modelo ORM da Avaliação.
Mapeia a tabela 'reviews' no banco de dados.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Review(Base):
    """
    Representa uma avaliação de um filme.
    Cada avaliação pertence a um usuário e a um filme.
    """
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Float, nullable=False)  # Nota de 1.0 a 10.0
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    movie = relationship("Movie", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
