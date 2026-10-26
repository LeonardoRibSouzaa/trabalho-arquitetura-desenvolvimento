from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReviewCreate(BaseModel):
    rating: float = Field(
        ..., ge=1.0, le=10.0,
        description="Nota do filme (de 1.0 a 10.0)",
        examples=[8.5]
    )
    comment: Optional[str] = Field(
        None, max_length=1000,
        description="Comentário ou resenha sobre o filme (opcional)",
        examples=["Filme incrível, atuações memoráveis!"]
    )


class ReviewResponse(BaseModel):
    id: int
    movie_id: int
    user_id: int
    rating: float
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
