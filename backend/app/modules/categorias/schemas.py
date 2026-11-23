from sqlmodel import SQLModel, Field
from pydantic import field_validator
from app.core.schemas import PartialUpdate


class CategoriaCreate(SQLModel):
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: str = ""

    @field_validator("nombre", mode="before")
    @classmethod
    def strip_name(cls, value):
        return value.strip() if isinstance(value, str) else value


class CategoriaUpdate(PartialUpdate):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    descripcion: str | None = None

    @field_validator("nombre", mode="before")
    @classmethod
    def strip_name(cls, value):
        return value.strip() if isinstance(value, str) else value


class CategoriaRead(CategoriaCreate):
    id: int
    activo: bool
