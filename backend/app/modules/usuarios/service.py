from app.core.errors import NotFound, DomainError
from app.modules.usuarios.schemas import UserPublic
from app.modules.usuarios.unit_of_work import UsuarioUnitOfWork


class UsuarioNoEncontrado(NotFound):
    pass


class UsuarioService:
    def __init__(self, uow=None):
        self.uow = uow or UsuarioUnitOfWork()

    def list(self):
        with self.uow as uow:
            return [UserPublic.model_validate(user) for user in uow.usuarios.get_all()]

    def set_disabled(self, identifier, disabled, actor):
        with self.uow as uow:
            user = uow.usuarios.get_by_id(identifier)
            if not user:
                raise UsuarioNoEncontrado("Usuario inexistente")
            if disabled and identifier == actor.id:
                raise DomainError("No podés desactivar tu propia cuenta")
            user.disabled = disabled
            uow.usuarios.add(user)
            return UserPublic.model_validate(user)
