from datetime import datetime
from typing import Literal
from sqlmodel import SQLModel, Field
from pydantic import field_validator


class ItemPedidoCreate(SQLModel):
    producto_id: int
    cantidad: int = Field(ge=1)


class PedidoCreate(SQLModel):
    items: list[ItemPedidoCreate] = Field(min_length=1)
    forma_pago: Literal["EFECTIVO", "TRANSFERENCIA"]
    direccion_entrega: str = Field(min_length=5, max_length=200)
    notas: str = ""

    @field_validator("direccion_entrega", mode="before")
    @classmethod
    def strip_address(cls, value):
        return value.strip() if isinstance(value, str) else value


class DetallePedidoRead(SQLModel):
    producto_id: int
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float


class PedidoRead(SQLModel):
    id: int
    usuario_id: int
    estado: str
    forma_pago: str
    direccion_entrega: str
    notas: str
    total: float
    created_at: datetime
    updated_at: datetime
    items: list[DetallePedidoRead]


class PedidosPaginados(SQLModel):
    total: int
    items: list[PedidoRead]


class CambioEstado(SQLModel):
    estado: Literal["PENDIENTE", "EN_PREPARACION", "ENTREGADO", "CANCELADO"]


class ResumenPedidos(SQLModel):
    pendientes: int
    en_preparacion: int
    entregados: int
    cancelados: int
    pedidos_hoy: int
    ingresos_entregados: float
