"""
Script de testes automatizados e geração de evidências para a CineTrack API.
Executa uma bateria completa de testes cobrindo todos os requisitos avaliados pelo roteiro:
- CRUD completo (GET coleção, GET individual/filtro, POST, PUT, DELETE)
- Autenticação e Segurança (Registro, Login, JWT, Endpoints protegidos, 401, 403)
- Qualidade HTTP e Tratamento de Erros (200, 201, 204, 400, 401, 403, 404, 409, 422)
- Validação de dados (Pydantic, regras de negócio)
- CORS (cabeçalhos de resposta)

Execução:
    python tests_and_evidence.py
"""

import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.movie import Movie
from app.models.review import Review

client = TestClient(app)

def reset_database():
    """Garante banco de dados limpo para os testes."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def log_test(step_num: int, title: str, method: str, url: str, status_expected: int, response):
    status_ok = response.status_code == status_expected
    mark = "PASSOU" if status_ok else "FALHOU"
    print(f"\n{'='*75}")
    print(f"[{mark}] Teste {step_num}: {title}")
    print(f"Requisição: {method} {url}")
    print(f"Status esperado: {status_expected} | Status obtido: {response.status_code}")
    try:
        data = response.json()
        print(f"Resposta JSON: {data}")
    except Exception:
        print(f"Corpo da resposta: {response.text}")
    print(f"{'='*75}")
    if not status_ok:
        print(f"ERRO: Esperava {status_expected}, mas obteve {response.status_code}")
        sys.exit(1)

def run_all_tests():
    print("=" * 75)
    print("INICIANDO BATERIA DE TESTES AUTOMATIZADOS - CINETRACK API")
    print("=" * 75)

    reset_database()
    step = 1

    # ---------------------------------------------------------
    # 1. AUTENTICAÇÃO: Registrar primeiro usuário (Alice)
    # ---------------------------------------------------------
    res = client.post("/auth/register", json={
        "username": "alice",
        "email": "alice@cinema.com",
        "password": "senhaSegura123"
    })
    log_test(step, "Registro de usuário válido (Alice)", "POST", "/auth/register", 201, res)
    step += 1

    # ---------------------------------------------------------
    # 2. VALIDAÇÃO: Tentar registrar usuário com mesmo username (409 Conflict)
    # ---------------------------------------------------------
    res = client.post("/auth/register", json={
        "username": "alice",
        "email": "outro@cinema.com",
        "password": "senhaSegura123"
    })
    log_test(step, "Tratamento de conflito - Username duplicado", "POST", "/auth/register", 409, res)
    step += 1

    # ---------------------------------------------------------
    # 3. VALIDAÇÃO: Registrar segundo usuário (Bob) para testes de permissão (403)
    # ---------------------------------------------------------
    res = client.post("/auth/register", json={
        "username": "bob",
        "email": "bob@cinema.com",
        "password": "senhaDoBob456"
    })
    log_test(step, "Registro de segundo usuário (Bob)", "POST", "/auth/register", 201, res)
    step += 1

    # ---------------------------------------------------------
    # 4. AUTENTICAÇÃO: Login com credenciais válidas (Alice) -> Obter JWT
    # ---------------------------------------------------------
    res = client.post("/auth/login", json={
        "username": "alice",
        "password": "senhaSegura123"
    })
    log_test(step, "Login bem-sucedido e emissão de token JWT", "POST", "/auth/login", 200, res)
    alice_token = res.json()["access_token"]
    alice_headers = {"Authorization": f"Bearer {alice_token}"}
    step += 1

    # ---------------------------------------------------------
    # 5. AUTENTICAÇÃO: Login de Bob
    # ---------------------------------------------------------
    res = client.post("/auth/login", json={
        "username": "bob",
        "password": "senhaDoBob456"
    })
    log_test(step, "Login de Bob para obter token", "POST", "/auth/login", 200, res)
    bob_token = res.json()["access_token"]
    bob_headers = {"Authorization": f"Bearer {bob_token}"}
    step += 1

    # ---------------------------------------------------------
    # 6. SEGURANÇA: Tentativa de login com senha incorreta (401 Unauthorized)
    # ---------------------------------------------------------
    res = client.post("/auth/login", json={
        "username": "alice",
        "password": "senhaErrada"
    })
    log_test(step, "Tratamento de erro - Credenciais inválidas", "POST", "/auth/login", 401, res)
    step += 1

    # ---------------------------------------------------------
    # 7. SEGURANÇA: Tentativa de criar filme sem autenticação (401 Unauthorized)
    # ---------------------------------------------------------
    res = client.post("/movies", json={
        "title": "Filme Não Autorizado",
        "genre": "ação",
        "year": 2020,
        "director": "Diretor X"
    })
    log_test(step, "Proteção de endpoint - Requisição sem Token JWT", "POST", "/movies", 401, res)
    step += 1

    # ---------------------------------------------------------
    # 8. CRUD - POST: Criar primeiro filme (Alice) (201 Created)
    # ---------------------------------------------------------
    res = client.post("/movies", headers=alice_headers, json={
        "title": "O Poderoso Chefão",
        "genre": "drama",
        "year": 1972,
        "director": "Francis Ford Coppola",
        "synopsis": "O patriarca de uma dinastia do crime transfere o império para o filho relutante."
    })
    log_test(step, "CRUD POST - Criação de filme com usuário autenticado", "POST", "/movies", 201, res)
    movie1_id = res.json()["id"]
    step += 1

    # ---------------------------------------------------------
    # 9. CRUD - POST: Criar segundo filme (Alice)
    # ---------------------------------------------------------
    res = client.post("/movies", headers=alice_headers, json={
        "title": "Interestelar",
        "genre": "ficção científica",
        "year": 2014,
        "director": "Christopher Nolan",
        "synopsis": "Exploradores viajam pelo espaço para garantir o futuro da humanidade."
    })
    log_test(step, "CRUD POST - Criação de segundo filme", "POST", "/movies", 201, res)
    movie2_id = res.json()["id"]
    step += 1

    # ---------------------------------------------------------
    # 10. VALIDAÇÃO: Tentar criar filme com gênero inválido (400 Bad Request)
    # ---------------------------------------------------------
    res = client.post("/movies", headers=alice_headers, json={
        "title": "Filme com Genero Estranho",
        "genre": "genero_inexistente_123",
        "year": 2020,
        "director": "Diretor Y"
    })
    log_test(step, "Validação de dados - Gênero inválido", "POST", "/movies", 400, res)
    step += 1

    # ---------------------------------------------------------
    # 11. VALIDAÇÃO: Tentar criar filme com ano inválido (422 Unprocessable Entity - Pydantic)
    # ---------------------------------------------------------
    res = client.post("/movies", headers=alice_headers, json={
        "title": "Filme do Futuro Distante",
        "genre": "ficção científica",
        "year": 2099,
        "director": "Diretor Z"
    })
    log_test(step, "Validação Pydantic - Ano fora do limite permitido", "POST", "/movies", 422, res)
    step += 1

    # ---------------------------------------------------------
    # 12. CRUD - GET: Listar coleção de recursos (200 OK)
    # ---------------------------------------------------------
    res = client.get("/movies")
    log_test(step, "CRUD GET - Listar coleção completa de filmes", "GET", "/movies", 200, res)
    step += 1

    # ---------------------------------------------------------
    # 13. CRUD - GET: Consultar recurso individual por ID (200 OK)
    # ---------------------------------------------------------
    res = client.get(f"/movies/{movie1_id}")
    log_test(step, "CRUD GET - Consultar filme individual por ID", "GET", f"/movies/{movie1_id}", 200, res)
    step += 1

    # ---------------------------------------------------------
    # 14. CRUD - GET com Filtragem Significativa: Filtrar por gênero drama
    # ---------------------------------------------------------
    res = client.get("/movies?genre=drama")
    log_test(step, "CRUD GET com filtro - Busca por gênero drama", "GET", "/movies?genre=drama", 200, res)
    step += 1

    # ---------------------------------------------------------
    # 15. TRATAMENTO DE ERRO: Consultar recurso inexistente (404 Not Found)
    # ---------------------------------------------------------
    res = client.get("/movies/9999")
    log_test(step, "Tratamento de erro - Filme não encontrado (404)", "GET", "/movies/9999", 404, res)
    step += 1

    # ---------------------------------------------------------
    # 16. SEGURANÇA E AUTORIZAÇÃO: Bob tenta editar filme da Alice (403 Forbidden)
    # ---------------------------------------------------------
    res = client.put(f"/movies/{movie1_id}", headers=bob_headers, json={
        "title": "Tentativa de Edição por Bob",
        "genre": "drama",
        "year": 1972,
        "director": "Francis Ford Coppola",
        "synopsis": "Tentativa indevida"
    })
    log_test(step, "Controle de Acesso - Usuário sem permissão tenta editar recurso (403)", "PUT", f"/movies/{movie1_id}", 403, res)
    step += 1

    # ---------------------------------------------------------
    # 17. CRUD - PUT: Alice atualiza seu próprio filme com sucesso (200 OK)
    # ---------------------------------------------------------
    res = client.put(f"/movies/{movie1_id}", headers=alice_headers, json={
        "title": "O Poderoso Chefão - Edição Restaurada",
        "genre": "drama",
        "year": 1972,
        "director": "Francis Ford Coppola",
        "synopsis": "Versão com imagem e áudio remasterizados em 4K."
    })
    log_test(step, "CRUD PUT - Atualização completa do recurso pelo proprietário", "PUT", f"/movies/{movie1_id}", 200, res)
    step += 1

    # ---------------------------------------------------------
    # 18. RECURSO SECUNDÁRIO: Bob avalia o filme de Alice (201 Created)
    # ---------------------------------------------------------
    res = client.post(f"/movies/{movie1_id}/reviews", headers=bob_headers, json={
        "rating": 10.0,
        "comment": "Melhor filme já feito! Atuação impecável."
    })
    log_test(step, "Criação de Avaliação (Review) para o filme", "POST", f"/movies/{movie1_id}/reviews", 201, res)
    step += 1

    # ---------------------------------------------------------
    # 19. RECURSO SECUNDÁRIO: Listar avaliações do filme
    # ---------------------------------------------------------
    res = client.get(f"/movies/{movie1_id}/reviews")
    log_test(step, "Listar avaliações associadas ao filme", "GET", f"/movies/{movie1_id}/reviews", 200, res)
    step += 1

    # ---------------------------------------------------------
    # 20. CRUD - DELETE: Bob tenta deletar filme da Alice (403 Forbidden)
    # ---------------------------------------------------------
    res = client.delete(f"/movies/{movie2_id}", headers=bob_headers)
    log_test(step, "Controle de Acesso - Bob tenta deletar filme da Alice (403)", "DELETE", f"/movies/{movie2_id}", 403, res)
    step += 1

    # ---------------------------------------------------------
    # 21. CRUD - DELETE: Alice deleta seu próprio filme (204 No Content)
    # ---------------------------------------------------------
    res = client.delete(f"/movies/{movie2_id}", headers=alice_headers)
    log_test(step, "CRUD DELETE - Remoção de recurso existente com 204 No Content", "DELETE", f"/movies/{movie2_id}", 204, res)
    step += 1

    # ---------------------------------------------------------
    # 22. TRATAMENTO DE ERRO: Verificar que filme deletado não existe mais (404)
    # ---------------------------------------------------------
    res = client.get(f"/movies/{movie2_id}")
    log_test(step, "Verificação pós-exclusão - Confirmar remoção (404 Not Found)", "GET", f"/movies/{movie2_id}", 404, res)
    step += 1

    # ---------------------------------------------------------
    # 23. CORS: Verificar cabeçalho Access-Control-Allow-Origin na resposta
    # ---------------------------------------------------------
    res = client.get("/", headers={"Origin": "http://meu-frontend.com"})
    cors_header = res.headers.get("access-control-allow-origin")
    assert cors_header == "*" or cors_header == "http://meu-frontend.com", "Cabeçalho CORS ausente!"
    print(f"\n{'='*75}")
    print(f"[PASSOU] Teste {step}: Verificação de cabeçalho CORS")
    print(f"Header retornado: access-control-allow-origin = {cors_header}")
    print(f"{'='*75}")

    print("\n" + "=" * 75)
    print("TODOS OS 23 TESTES FORAM EXECUTADOS COM SUCESSO! 100% DE APROVAÇÃO!")
    print("=" * 75)

if __name__ == "__main__":
    run_all_tests()
