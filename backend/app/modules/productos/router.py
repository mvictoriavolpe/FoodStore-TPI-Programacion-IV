from fastapi import APIRouter, Depends, Query, Response
from app.core.deps import require_role
from app.core.errors import translate_errors
from app.modules.productos.schemas import (
    ProductoCreate,
    ProductoUpdate,
    ProductoStockUpdate,
    ProductoRead,
    ProductosPaginados,
)
from app.modules.productos.service import ProductoService

router = APIRouter(prefix="/productos", tags=["productos"])


def get_producto_service():
    return ProductoService()


@router.get("", response_model=ProductosPaginados)
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
    categoria_id: int | None = None,
    disponible: bool | None = None,
    service: ProductoService = Depends(get_producto_service),
):
    with translate_errors():
        return service.list(
            skip=skip,
            limit=limit,
            search=search,
            categoria_id=categoria_id,
            disponible=disponible,
        )


@router.get("/{id}", response_model=ProductoRead)
def get_product(id: int, service: ProductoService = Depends(get_producto_service)):
    with translate_errors():
        return service.get(id)


@router.post(
    "",
    status_code=201,
    response_model=ProductoRead,
    dependencies=[Depends(require_role(["admin"]))],
)
def create_product(
    data: ProductoCreate, service: ProductoService = Depends(get_producto_service)
):
    with translate_errors():
        return service.save(data)


@router.put(
    "/{id}",
    response_model=ProductoRead,
    dependencies=[Depends(require_role(["admin"]))],
)
def update_product(
    id: int,
    data: ProductoUpdate,
    service: ProductoService = Depends(get_producto_service),
):
    with translate_errors():
        return service.save(data, id)


@router.patch(
    "/{id}/stock",
    response_model=ProductoRead,
    dependencies=[Depends(require_role(["admin"]))],
)
def update_stock(
    id: int,
    data: ProductoStockUpdate,
    service: ProductoService = Depends(get_producto_service),
):
    with translate_errors():
        return service.save(data, id)


@router.delete(
    "/{id}", status_code=204, dependencies=[Depends(require_role(["admin"]))]
)
def delete_product(id: int, service: ProductoService = Depends(get_producto_service)):
    with translate_errors():
        service.delete(id)
    return Response(status_code=204)
