from fastapi import HTTPException

from app.core.errors import Conflict
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import UserPublic
from app.modules.usuarios.unit_of_work import UsuarioUnitOfWork


class UsuarioDuplicado(Conflict):
    pass


class AuthService:
    def __init__(self, uow=None):
        self.uow = uow or UsuarioUnitOfWork()

    def register(self, data):
        with self.uow as uow:
            if uow.usuarios.get_by_username(data.username) or uow.usuarios.get_by_email(
                str(data.email)
            ):
                raise UsuarioDuplicado("Usuario o email duplicado")
            user = Usuario(
                username=data.username,
                full_name=data.full_name,
                email=str(data.email),
                hashed_password=hash_password(data.password),
                role="user",
            )
            uow.usuarios.add(user)
            return UserPublic.model_validate(user)

    def login(self, username, password):
        with self.uow as uow:
            user = uow.usuarios.get_by_username(username)
            if not user or not verify_password(password, user.hashed_password):
                raise HTTPException(401, "Credenciales incorrectas")
            if user.disabled:
                raise HTTPException(400, "Cuenta de usuario desactivada")
            return create_access_token(user.username)
