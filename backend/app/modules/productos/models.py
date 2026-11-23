from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.modules.categorias.models import Categoria

if TYPE_CHECKING:
    from app.modules.pedidos.models import DetallePedido


class Producto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    categoria_id: int = Field(foreign_key="categoria.id")
    nombre: str
    descripcion: str = ""
    precio_base: float = Field(ge=0)
    imagen_url: str = ""
    stock: int = Field(default=0, ge=0)
    disponible: bool = True
    activo: bool = True
    categoria: Categoria = Relationship(back_populates="productos")
    detalles: list["DetallePedido"] = Relationship(back_populates="producto")
