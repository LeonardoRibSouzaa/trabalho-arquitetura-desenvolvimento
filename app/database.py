"""
Módulo de conexão com o banco de dados.
Configura o engine do SQLAlchemy, a sessão e a classe base para os modelos ORM.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import DATABASE_URL

# Cria o engine de conexão com o banco de dados
# check_same_thread=False é necessário para SQLite funcionar com FastAPI (multithreaded)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Fábrica de sessões do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base declarativa para todos os modelos ORM da aplicação."""
    pass


def get_db():
    """
    Dependency injection do FastAPI para fornecer uma sessão do banco de dados.
    Garante que a sessão é fechada após o uso, mesmo em caso de erro.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
