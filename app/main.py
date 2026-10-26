"""
CineTrack API — Ponto de entrada da aplicação.
Configura FastAPI, CORS, routers e handlers globais de exceção.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import engine, Base
from app.routers import auth, movies, reviews

# Cria todas as tabelas no banco de dados (se não existirem)
Base.metadata.create_all(bind=engine)

# Instância principal da aplicação FastAPI
app = FastAPI(
    title="CineTrack API",
    description=(
        "API RESTful para gerenciamento de catálogo pessoal de filmes e avaliações. "
        "Desenvolvida como trabalho prático da disciplina de Arquitetura e Desenvolvimento de APIs — Uninter."
    ),
    version="1.0.0",
    contact={"name": "Estudante Uninter"},
    docs_url="/docs",
    redoc_url="/redoc",
)

# =====================================================================
# CONFIGURAÇÃO DO CORS (Cross-Origin Resource Sharing)
# =====================================================================
# Política: liberação irrestrita de todas as origens, métodos e cabeçalhos.
#
# Justificativa: Como esta API não possui um frontend próprio hospedado
# em outro domínio, e será testada via Swagger UI, Postman ou cURL,
# a liberação irrestrita é adequada para o ambiente de desenvolvimento.
# Em um cenário de produção, as origens deveriam ser restritas aos
# domínios específicos do(s) frontend(s) consumidor(es) da API.
# =====================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Permite qualquer origem
    allow_credentials=True,    # Permite envio de cookies/credenciais
    allow_methods=["*"],       # Permite todos os métodos HTTP
    allow_headers=["*"],       # Permite todos os cabeçalhos
)

# Registra os routers de cada recurso
app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(reviews.router)


# Handler global de exceções não tratadas
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Captura qualquer exceção não tratada e retorna uma resposta 500
    genérica, evitando expor detalhes internos ao cliente.
    """
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor. Tente novamente mais tarde."}
    )


@app.get("/", tags=["Root"], summary="Rota raiz da API")
def root():
    """
    Endpoint raiz que retorna informações básicas sobre a API
    e o link para a documentação interativa.
    """
    return {
        "api": "CineTrack",
        "versao": "1.0.0",
        "descricao": "API de catálogo de filmes e avaliações",
        "documentacao": "/docs"
    }
