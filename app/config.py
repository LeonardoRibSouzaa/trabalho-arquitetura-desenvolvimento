"""
Módulo de configuração da aplicação.
Carrega variáveis de ambiente do arquivo .env e define valores padrão.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# URL de conexão com o banco de dados SQLite
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cinetrack.db")

# Chave secreta para assinatura dos tokens JWT
SECRET_KEY: str = os.getenv("SECRET_KEY", "chave-secreta-padrao-troque-em-producao")

# Algoritmo de criptografia do JWT
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

# Tempo de expiração do token em minutos
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
