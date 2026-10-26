from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.movie import Movie
from app.models.review import Review
from app.auth.security import hash_password


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(User).first():
            print("Banco ja contem dados.")
            return

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
            genre="suspense",
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

        print("Seed concluido com sucesso.")

    except Exception as e:
        db.rollback()
        print(f"Erro durante o seed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
