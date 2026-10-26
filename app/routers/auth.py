"""
Router de autenticação.
Endpoints para registro de usuários e login com JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.auth.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="Cria um novo usuário no sistema. O username e o e-mail devem ser únicos."
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário no sistema.

    - **username**: Nome de usuário único (3 a 50 caracteres)
    - **email**: E-mail válido e único
    - **password**: Senha com no mínimo 6 caracteres (armazenada como hash bcrypt)
    """
    # Verifica se username já existe
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nome de usuário já cadastrado"
        )

    # Verifica se email já existe
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado"
        )

    # Cria o novo usuário com senha hasheada
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post(
    "/login",
    response_model=Token,
    summary="Fazer login e obter token JWT",
    description="Autentica o usuário e retorna um token JWT para acesso aos endpoints protegidos."
)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Realiza o login do usuário.

    - **username**: Nome de usuário cadastrado
    - **password**: Senha do usuário

    Retorna um token JWT válido por 30 minutos (configurável via variável de ambiente).
    """
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

