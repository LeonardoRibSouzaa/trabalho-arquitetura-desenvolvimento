"""
Modelo ORM do Usuário.
Mapeia a tabela 'users' no banco de dados.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """
    Representa um usuário da aplicação.
    Cada usuário pode cadastrar filmes e criar avaliações.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos: um usuário pode ter vários filmes e várias avaliações
    movies = relationship("Movie", back_populates="creator")
    reviews = relationship("Review", back_populates="user")
