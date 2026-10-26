"""
Script para popular o banco de dados inicial com dados de exemplo (Seed).
Útil para testes imediatos e avaliação do professor.

Execução:
    python seed.py
"""

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.movie import Movie
from app.models.review import Review
from app.auth.security import hash_password


def seed_database():
    print("Iniciando criação de tabelas e inserção de dados de exemplo...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Verifica se já existem dados
        if db.query(User).first():
            print("O banco de dados já possui registros cadastrados. Seed cancelado.")
            return

        # 1. Criação de usuários de teste
        user1 = User(
            username="aluno_avaliador",
            email="aluno@uninter.com",
            hashed_password=hash_password("senha123")
        )
        user2 = User(
            username="cinefilo_pro",
            email="cinefilo@cinema.com",
            hashed_password=hash_password("senha123")
        )
        db.add_all([user1, user2])
        db.commit()
        db.refresh(user1)
        db.refresh(user2)

        # 2. Criação de filmes de exemplo
        movie1 = Movie(
            title="O Poderoso Chefão",
            genre="drama",
            year=1972,
            director="Francis Ford Coppola",
            synopsis="O patriarca idoso de uma dinastia do crime organizado transfere o controle de seu império clandestino para seu filho relutante.",
            created_by=user1.id
        )
        movie2 = Movie(
            title="Interestelar",
            genre="ficção científica",
            year=2014,
            director="Christopher Nolan",
            synopsis="Uma equipe de exploradores viaja através de um buraco de minhoca no espaço, na tentativa de garantir a sobrevivência da humanidade.",
            created_by=user1.id
        )
        movie3 = Movie(
            title="Pulp Fiction: Tempo de Violência",
            genre="crime",
            year=1994,
            director="Quentin Tarantino",
            synopsis="As vidas de dois assassinos da máfia, um boxeador e um casal de assaltantes se entrelaçam em quatro histórias de violência e redenção.",
            created_by=user2.id
        )
        db.add_all([movie1, movie2, movie3])
        db.commit()
        db.refresh(movie1)
        db.refresh(movie2)
        db.refresh(movie3)

        # 3. Criação de avaliações de exemplo
        review1 = Review(
            movie_id=movie1.id,
            user_id=user2.id,
            rating=10.0,
            comment="Uma verdadeira obra-prima do cinema mundial. Atuações lendárias de Marlon Brando e Al Pacino."
        )
        review2 = Review(
            movie_id=movie2.id,
            user_id=user1.id,
            rating=9.5,
            comment="Trilha sonora marcante de Hans Zimmer e conceito visual fascinante sobre relatividade do tempo."
        )
        db.add_all([review1, review2])
        db.commit()

        print("Dados de exemplo inseridos com sucesso!")
        print("\nUsuários para teste:")
        print("  - Username: aluno_avaliador | Senha: senha123")
        print("  - Username: cinefilo_pro   | Senha: senha123")
        print("\nFilmes inseridos: 3")
        print("Avaliações inseridas: 2")

    except Exception as e:
        db.rollback()
        print(f"Erro durante o seed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
