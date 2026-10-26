from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50,
        description="Nome de usuário (3 a 50 caracteres)",
        examples=["joaosilva"]
    )
    email: EmailStr = Field(
        ..., description="E-mail válido do usuário",
        examples=["joao@email.com"]
    )
    password: str = Field(
        ..., min_length=6,
        description="Senha do usuário (mínimo 6 caracteres)",
        examples=["minhaSenha123"]
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str = Field(..., description="Nome de usuário", examples=["joaosilva"])
    password: str = Field(..., description="Senha do usuário", examples=["minhaSenha123"])
