import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
from app.models.user import User
from app.models.movie import Movie
from app.models.review import Review

client = TestClient(app)

def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def log_test(step_num, title, method, url, status_expected, response):
    status_ok = response.status_code == status_expected
    mark = "OK" if status_ok else "FALHOU"
    print(f"[{mark}] Teste {step_num}: {title} | {method} {url} -> {response.status_code}")
    if not status_ok:
        print(f"ERRO: Esperava {status_expected}, mas obteve {response.status_code}")
        print(f"Corpo: {response.text}")
        sys.exit(1)

def run_all_tests():
    print("Iniciando testes da API...")
    reset_database()
    step = 1

    res = client.post("/auth/register", json={
        "username": "alice",
        "email": "alice@cinema.com",
        "password": "senhaSegura123"
    })
    log_test(step, "Registro de usuario valido (Alice)", "POST", "/auth/register", 201, res)
    step += 1

    res = client.post("/auth/register", json={
        "username": "alice",
        "email": "outro@cinema.com",
        "password": "senhaSegura123"
    })
    log_test(step, "Conflito de username duplicado", "POST", "/auth/register", 409, res)
    step += 1

    res = client.post("/auth/register", json={
        "username": "bob",
        "email": "bob@cinema.com",
        "password": "senhaDoBob456"
    })
    log_test(step, "Registro de segundo usuario (Bob)", "POST", "/auth/register", 201, res)
    step += 1

    res = client.post("/auth/login", json={
        "username": "alice",
        "password": "senhaSegura123"
    })
    log_test(step, "Login com sucesso e geracao de JWT", "POST", "/auth/login", 200, res)
    alice_token = res.json()["access_token"]
    alice_headers = {"Authorization": f"Bearer {alice_token}"}
    step += 1

    res = client.post("/auth/login", json={
        "username": "bob",
        "password": "senhaDoBob456"
    })
    log_test(step, "Login de Bob", "POST", "/auth/login", 200, res)
    bob_token = res.json()["access_token"]
    bob_headers = {"Authorization": f"Bearer {bob_token}"}
    step += 1

    res = client.post("/auth/login", json={
        "username": "alice",
        "password": "senhaErrada"
    })
    log_test(step, "Login com senha incorreta", "POST", "/auth/login", 401, res)
    step += 1

    res = client.post("/movies", json={
        "title": "Filme Nao Autorizado",
        "genre": "ação",
        "year": 2020,
        "director": "Diretor X"
    })
    log_test(step, "Tentativa de criar filme sem autenticacao", "POST", "/movies", 401, res)
    step += 1

    res = client.post("/movies", headers=alice_headers, json={
        "title": "O Poderoso Chefão",
        "genre": "drama",
        "year": 1972,
        "director": "Francis Ford Coppola",
        "synopsis": "O patriarca de uma dinastia do crime transfere o império para o filho relutante."
    })
    log_test(step, "Criacao de filme com usuario autenticado", "POST", "/movies", 201, res)
    movie1_id = res.json()["id"]
    step += 1

    res = client.post("/movies", headers=alice_headers, json={
        "title": "Interestelar",
        "genre": "ficção científica",
        "year": 2014,
        "director": "Christopher Nolan",
        "synopsis": "Exploradores viajam pelo espaço para garantir o futuro da humanidade."
    })
    log_test(step, "Criacao de segundo filme", "POST", "/movies", 201, res)
    movie2_id = res.json()["id"]
    step += 1

    res = client.post("/movies", headers=alice_headers, json={
        "title": "Filme com Genero Invalido",
        "genre": "genero_inexistente_123",
        "year": 2020,
        "director": "Diretor Y"
    })
    log_test(step, "Validacao de genero invalido", "POST", "/movies", 400, res)
    step += 1

    res = client.post("/movies", headers=alice_headers, json={
        "title": "Filme com Ano Invalido",
        "genre": "ficção científica",
        "year": 2099,
        "director": "Diretor Z"
    })
    log_test(step, "Validacao Pydantic de ano fora do limite", "POST", "/movies", 422, res)
    step += 1

    res = client.get("/movies")
    log_test(step, "Listagem de filmes", "GET", "/movies", 200, res)
    step += 1

    res = client.get(f"/movies/{movie1_id}")
    log_test(step, "Consulta de filme por ID", "GET", f"/movies/{movie1_id}", 200, res)
    step += 1

    res = client.get("/movies?genre=drama")
    log_test(step, "Filtro de filmes por genero", "GET", "/movies?genre=drama", 200, res)
    step += 1

    res = client.get("/movies/9999")
    log_test(step, "Consulta de filme inexistente", "GET", "/movies/9999", 404, res)
    step += 1

    res = client.put(f"/movies/{movie1_id}", headers=bob_headers, json={
        "title": "Tentativa de Edicao por Bob",
        "genre": "drama",
        "year": 1972,
        "director": "Francis Ford Coppola",
        "synopsis": "Tentativa indevida"
    })
    log_test(step, "Bloqueio de edicao por outro usuario", "PUT", f"/movies/{movie1_id}", 403, res)
    step += 1

    res = client.put(f"/movies/{movie1_id}", headers=alice_headers, json={
        "title": "O Poderoso Chefão - Edição Restaurada",
        "genre": "drama",
        "year": 1972,
        "director": "Francis Ford Coppola",
        "synopsis": "Versão com imagem e áudio remasterizados em 4K."
    })
    log_test(step, "Atualizacao de filme pelo criador", "PUT", f"/movies/{movie1_id}", 200, res)
    step += 1

    res = client.post(f"/movies/{movie1_id}/reviews", headers=bob_headers, json={
        "rating": 10.0,
        "comment": "Melhor filme já feito! Atuação impecável."
    })
    log_test(step, "Criacao de avaliacao para o filme", "POST", f"/movies/{movie1_id}/reviews", 201, res)
    step += 1

    res = client.get(f"/movies/{movie1_id}/reviews")
    log_test(step, "Listagem de avaliacoes do filme", "GET", f"/movies/{movie1_id}/reviews", 200, res)
    step += 1

    res = client.delete(f"/movies/{movie2_id}", headers=bob_headers)
    log_test(step, "Bloqueio de exclusao por outro usuario", "DELETE", f"/movies/{movie2_id}", 403, res)
    step += 1

    res = client.delete(f"/movies/{movie2_id}", headers=alice_headers)
    log_test(step, "Exclusao de filme pelo criador", "DELETE", f"/movies/{movie2_id}", 204, res)
    step += 1

    res = client.get(f"/movies/{movie2_id}")
    log_test(step, "Verificacao de filme excluido", "GET", f"/movies/{movie2_id}", 404, res)
    step += 1

    res = client.get("/", headers={"Origin": "http://meu-frontend.com"})
    cors_header = res.headers.get("access-control-allow-origin")
    assert cors_header == "*" or cors_header == "http://meu-frontend.com", "Header CORS ausente"
    log_test(step, "Validacao do header CORS", "GET", "/", 200, res)

    print("\nTodos os 23 testes executados com sucesso.")


if __name__ == "__main__":
    run_all_tests()
