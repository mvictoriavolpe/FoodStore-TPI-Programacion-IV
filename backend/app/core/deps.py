from fastapi import Depends, HTTPException, Request
from jose import JWTError

from app.core.security import decode_access_token
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.unit_of_work import UsuarioUnitOfWork


def get_current_user(request: Request) -> Usuario:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "No autenticado")
    try:
        username = decode_access_token(token)["sub"]
    except (JWTError, KeyError, TypeError) as error:
        raise HTTPException(401, "Token inválido o vencido") from error
    with UsuarioUnitOfWork() as uow:
        user = uow.usuarios.get_by_username(username)
        if user is None:
            raise HTTPException(401, "Sesión inválida")
        uow.session.expunge(user)
        return user


def get_current_active_user(user: Usuario = Depends(get_current_user)) -> Usuario:
    if user.disabled:
        raise HTTPException(400, "Cuenta de usuario desactivada")
    return user


def require_role(roles: list[str]):
    def check(user: Usuario = Depends(get_current_active_user)) -> Usuario:
        if user.role not in roles:
            raise HTTPException(403, "No autorizado")
        return user

    return check
