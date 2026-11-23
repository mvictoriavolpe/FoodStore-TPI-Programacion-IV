from typing import Literal
from fastapi import APIRouter, Depends, Query
from app.core.deps import get_current_active_user, require_role
from app.core.errors import translate_errors
from app.modules.usuarios.models import Usuario
from app.modules.pedidos.schemas import (
    PedidoCreate,
    PedidoRead,
    PedidosPaginados,
    CambioEstado,
    ResumenPedidos,
)
from app.modules.pedidos.service import PedidoService

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


def get_pedido_service():
    return PedidoService()


@router.post("", status_code=201, response_model=PedidoRead)
def create_order(
    data: PedidoCreate,
    user: Usuario = Depends(get_current_active_user),
    service: PedidoService = Depends(get_pedido_service),
):
    with translate_errors():
        return service.create(data, user)


@router.get("", response_model=PedidosPaginados)
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    estado: (
        Literal["PENDIENTE", "EN_PREPARACION", "ENTREGADO", "CANCELADO"] | None
    ) = None,
    user: Usuario = Depends(get_current_active_user),
    service: PedidoService = Depends(get_pedido_service),
):
    with translate_errors():
        return service.list(user, skip=skip, limit=limit, estado=estado)


@router.get("/resumen", response_model=ResumenPedidos)
def summary(
    user: Usuario = Depends(require_role(["admin"])),
    service: PedidoService = Depends(get_pedido_service),
):
    with translate_errors():
        return service.summary()


@router.get("/{id}", response_model=PedidoRead)
def get_order(
    id: int,
    user: Usuario = Depends(get_current_active_user),
    service: PedidoService = Depends(get_pedido_service),
):
    with translate_errors():
        return service.get(id, user)


@router.patch("/{id}/estado", response_model=PedidoRead)
def change_state(
    id: int,
    data: CambioEstado,
    user: Usuario = Depends(require_role(["admin"])),
    service: PedidoService = Depends(get_pedido_service),
):
    with translate_errors():
        return service.change_state(id, data.estado, user)


@router.patch("/{id}/cancelar", response_model=PedidoRead)
def cancel(
    id: int,
    user: Usuario = Depends(get_current_active_user),
    service: PedidoService = Depends(get_pedido_service),
):
    with translate_errors():
        return service.change_state(id, "CANCELADO", user, own=True)
