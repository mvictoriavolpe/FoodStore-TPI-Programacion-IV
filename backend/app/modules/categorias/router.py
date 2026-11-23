from fastapi import APIRouter, Depends, Response
from app.core.deps import require_role
from app.core.errors import translate_errors
from app.modules.categorias.schemas import (
    CategoriaCreate,
    CategoriaUpdate,
    CategoriaRead,
)
from app.modules.categorias.service import CategoriaService

router = APIRouter(prefix="/categorias", tags=["categorias"])


def get_categoria_service():
    return CategoriaService()


@router.get("", response_model=list[CategoriaRead])
def list_categories(service: CategoriaService = Depends(get_categoria_service)):
    with translate_errors():
        return service.list()


@router.get("/{id}", response_model=CategoriaRead)
def get_category(id: int, service: CategoriaService = Depends(get_categoria_service)):
    with translate_errors():
        return service.get(id)


@router.post(
    "",
    status_code=201,
    response_model=CategoriaRead,
    dependencies=[Depends(require_role(["admin"]))],
)
def create_category(
    data: CategoriaCreate, service: CategoriaService = Depends(get_categoria_service)
):
    with translate_errors():
        return service.save(data)


@router.put(
    "/{id}",
    response_model=CategoriaRead,
    dependencies=[Depends(require_role(["admin"]))],
)
def update_category(
    id: int,
    data: CategoriaUpdate,
    service: CategoriaService = Depends(get_categoria_service),
):
    with translate_errors():
        return service.save(data, id)


@router.delete(
    "/{id}", status_code=204, dependencies=[Depends(require_role(["admin"]))]
)
def delete_category(
    id: int, service: CategoriaService = Depends(get_categoria_service)
):
    with translate_errors():
        service.delete(id)
    return Response(status_code=204)
