from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.modules.productos.models import Producto


class Categoria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True)
    descripcion: str = ""
    activo: bool = True
    productos: list["Producto"] = Relationship(back_populates="categoria")
