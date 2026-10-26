# 🎬 CineTrack API

API RESTful para gerenciamento de catálogo pessoal de filmes e avaliações.

Desenvolvida como trabalho prático da disciplina de **Arquitetura e Desenvolvimento de APIs** do Centro Universitário Internacional Uninter.

---

## 📋 Descrição

A CineTrack é uma API que permite aos usuários:
- Cadastrar filmes assistidos com informações como título, gênero, ano, diretor e sinopse
- Criar avaliações (notas e comentários) para os filmes cadastrados
- Consultar, filtrar, atualizar e remover filmes do catálogo
- Controle de acesso via autenticação JWT

**Público-alvo**: Entusiastas de cinema que desejam manter um catálogo pessoal organizado dos filmes que assistiram, com notas e resenhas.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Finalidade |
|---|---|---|
| Python | 3.10+ | Linguagem de programação |
| FastAPI | 0.104.1 | Framework web para APIs |
| SQLAlchemy | 2.0.23 | ORM (mapeamento objeto-relacional) |
| SQLite | 3 | Banco de dados relacional |
| Pydantic | 2.5.2 | Validação de dados |
| python-jose | 3.3.0 | Geração e validação de tokens JWT |
| passlib + bcrypt | 1.7.4 | Hashing de senhas |
| Uvicorn | 0.24.0 | Servidor ASGI |

---

## 📦 Pré-requisitos

- **Python 3.10 ou superior** instalado ([download](https://www.python.org/downloads/))
- **pip** (gerenciador de pacotes do Python — já vem com o Python)
- **Git** (para clonar o repositório)

---

## 🚀 Instalação e Execução

### 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd cinetrack-api
```

### 2. Criar ambiente virtual (recomendado)

```bash
python -m venv venv
```

Ativar o ambiente:

- **Windows**: `venv\Scripts\activate`
- **Linux/Mac**: `source venv/bin/activate`

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Copie o arquivo de exemplo e ajuste se necessário:

```bash
cp .env.example .env
```

> ⚠️ Em produção, altere a `SECRET_KEY` para uma chave segura e única.

### 5. Iniciar a aplicação

```bash
uvicorn app.main:app --reload
```

A API estará disponível em: **http://127.0.0.1:8000**

### 6. Acessar a documentação

- **Swagger UI (interativo)**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

---

## 🗄️ Banco de Dados

O banco de dados utilizado é o **SQLite**, que é criado automaticamente ao iniciar a aplicação (arquivo `cinetrack.db` na raiz do projeto). Não é necessária nenhuma instalação de SGBD externo.

As tabelas são criadas automaticamente pelo SQLAlchemy através do comando `Base.metadata.create_all()` no arquivo `main.py`.

### Povoamento Inicial (Seed - Opcional)

Para popular o banco com usuários, filmes e avaliações de exemplo para testes imediatos:

```bash
python seed.py
```

Isso criará:
- Usuários: `aluno_avaliador` (senha: `senha123`) e `cinefilo_pro` (senha: `senha123`)
- 3 filmes clássicos com gêneros e anos variados
- 2 avaliações com notas e comentários

---

## 🧪 Testes Automatizados e Evidências

A aplicação conta com uma suíte de testes automatizados completa cobrindo 23 cenários (CRUD, JWT, 401, 403, 404, validações e CORS):

```bash
python tests_and_evidence.py
```

Todos os testes validam códigos HTTP, formato JSON das respostas e regras de permissão.


## 🔐 Autenticação

A API utiliza **JWT (JSON Web Tokens)** para autenticação.

### Fluxo:

1. **Registrar** um usuário em `POST /auth/register`
2. **Fazer login** em `POST /auth/login` → recebe um `access_token`
3. **Usar o token** no header `Authorization: Bearer <token>` para acessar endpoints protegidos

### Credenciais de teste:

Você pode criar seu próprio usuário via endpoint de registro. Exemplo:

```json
{
  "username": "testuser",
  "email": "test@email.com",
  "password": "senha123"
}
```

> ⚠️ O token expira em 30 minutos (configurável via `.env`).

---

## 📍 Resumo dos Endpoints

### Autenticação

| Método | Endpoint | Finalidade | Autenticação |
|---|---|---|---|
| POST | `/auth/register` | Registrar novo usuário | ❌ Não |
| POST | `/auth/login` | Login (obter token JWT) | ❌ Não |

### Filmes (Recurso Principal)

| Método | Endpoint | Finalidade | Autenticação |
|---|---|---|---|
| GET | `/movies` | Listar filmes (com filtros) | ❌ Não |
| GET | `/movies/{id}` | Consultar filme por ID | ❌ Não |
| POST | `/movies` | Criar novo filme | ✅ JWT |
| PUT | `/movies/{id}` | Atualizar filme | ✅ JWT |
| DELETE | `/movies/{id}` | Excluir filme | ✅ JWT |

### Avaliações

| Método | Endpoint | Finalidade | Autenticação |
|---|---|---|---|
| GET | `/movies/{id}/reviews` | Listar avaliações de um filme | ❌ Não |
| POST | `/movies/{id}/reviews` | Criar avaliação | ✅ JWT |

---

## 📝 Exemplos de Requisição (cURL)

### Registrar usuário

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "joao", "email": "joao@email.com", "password": "senha123"}'
```

### Fazer login

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "joao", "password": "senha123"}'
```

Resposta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Criar um filme (com token)

```bash
curl -X POST http://127.0.0.1:8000/movies \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "title": "O Poderoso Chefão",
    "genre": "drama",
    "year": 1972,
    "director": "Francis Ford Coppola",
    "synopsis": "A história da família Corleone e do submundo da máfia."
  }'
```

### Listar filmes (com filtro)

```bash
curl "http://127.0.0.1:8000/movies?genre=drama&page=1&limit=5"
```

### Consultar filme por ID

```bash
curl http://127.0.0.1:8000/movies/1
```

### Atualizar filme

```bash
curl -X PUT http://127.0.0.1:8000/movies/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "title": "O Poderoso Chefão - Parte I",
    "genre": "drama",
    "year": 1972,
    "director": "Francis Ford Coppola",
    "synopsis": "A história da família Corleone."
  }'
```

### Excluir filme

```bash
curl -X DELETE http://127.0.0.1:8000/movies/1 \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Criar avaliação

```bash
curl -X POST http://127.0.0.1:8000/movies/1/reviews \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{"rating": 9.5, "comment": "Obra-prima do cinema!"}'
```

---

## 📁 Estrutura do Projeto

```
cinetrack-api/
├── app/
│   ├── __init__.py           # Pacote app
│   ├── main.py               # Entry point, CORS, exception handlers
│   ├── config.py             # Configurações (variáveis de ambiente)
│   ├── database.py           # Conexão SQLAlchemy e sessão
│   ├── models/               # Modelos ORM
│   │   ├── __init__.py
│   │   ├── user.py           # Modelo User
│   │   ├── movie.py          # Modelo Movie
│   │   └── review.py         # Modelo Review
│   ├── schemas/              # Schemas Pydantic (validação)
│   │   ├── __init__.py
│   │   ├── user.py           # Schemas de usuário
│   │   ├── movie.py          # Schemas de filme
│   │   └── review.py         # Schemas de avaliação
│   ├── routers/              # Endpoints organizados por recurso
│   │   ├── __init__.py
│   │   ├── auth.py           # Registro e login
│   │   ├── movies.py         # CRUD de filmes
│   │   └── reviews.py        # Avaliações de filmes
│   └── auth/                 # Módulo de autenticação
│       ├── __init__.py
│       └── security.py       # JWT e hashing bcrypt
├── .env.example              # Exemplo de variáveis de ambiente
├── .gitignore                # Arquivos ignorados pelo Git
├── requirements.txt          # Dependências Python
└── README.md                 # Este arquivo
```

---

## 📄 Licença

Projeto desenvolvido para fins acadêmicos.
