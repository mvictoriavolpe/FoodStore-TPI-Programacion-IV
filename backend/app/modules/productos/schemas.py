from sqlmodel import SQLModel, Field
from pydantic import field_validator, FiniteFloat
from app.modules.categorias.schemas import CategoriaRead
from app.core.schemas import PartialUpdate


class ProductoCreate(SQLModel):
    categoria_id: int
    nombre: str = Field(min_length=1)
    descripcion: str = ""
    precio_base: FiniteFloat = Field(ge=0)
    imagen_url: str = ""
    stock: int = Field(default=0, ge=0)
    disponible: bool = True

    @field_validator("nombre", mode="before")
    @classmethod
    def strip_name(cls, value):
        return value.strip() if isinstance(value, str) else value


class ProductoUpdate(PartialUpdate):
    categoria_id: int | None = None
    nombre: str | None = Field(default=None, min_length=1)
    descripcion: str | None = None
    precio_base: FiniteFloat | None = Field(default=None, ge=0)
    imagen_url: str | None = None
    stock: int | None = Field(default=None, ge=0)
    disponible: bool | None = None

    @field_validator("nombre", mode="before")
    @classmethod
    def strip_name(cls, value):
        return value.strip() if isinstance(value, str) else value


class ProductoStockUpdate(SQLModel):
    stock: int = Field(ge=0)
    disponible: bool


class ProductoRead(ProductoCreate):
    id: int
    activo: bool
    categoria: CategoriaRead


class ProductosPaginados(SQLModel):
    total: int
    items: list[ProductoRead]
