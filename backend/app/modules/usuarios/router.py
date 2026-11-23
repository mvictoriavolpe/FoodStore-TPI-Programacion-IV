from fastapi import APIRouter, Depends
from app.core.deps import require_role
from app.core.errors import translate_errors
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import UserPublic
from app.modules.usuarios.service import UsuarioService

router = APIRouter(prefix="/admin/usuarios", tags=["usuarios"])


def get_usuario_service():
    return UsuarioService()


@router.get("", response_model=list[UserPublic])
def users(
    actor: Usuario = Depends(require_role(["admin"])),
    service: UsuarioService = Depends(get_usuario_service),
):
    with translate_errors():
        return service.list()


@router.post("/{id}/activar", response_model=UserPublic)
def activate(
    id: int,
    actor: Usuario = Depends(require_role(["admin"])),
    service: UsuarioService = Depends(get_usuario_service),
):
    with translate_errors():
        return service.set_disabled(id, False, actor)


@router.post("/{id}/desactivar", response_model=UserPublic)
def deactivate(
    id: int,
    actor: Usuario = Depends(require_role(["admin"])),
    service: UsuarioService = Depends(get_usuario_service),
):
    with translate_errors():
        return service.set_disabled(id, True, actor)
