from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.deps import get_current_active_user
from app.core.errors import translate_errors
from app.modules.auth.schemas import UserCreate, UserPublic
from app.modules.auth.service import AuthService
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service():
    return AuthService()


@router.post("/register", status_code=201, response_model=UserPublic)
def register(data: UserCreate, service: AuthService = Depends(get_auth_service)):
    with translate_errors():
        return service.register(data)


@router.post("/token")
def login(
    response: Response,
    form: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    with translate_errors():
        token = service.login(form.username, form.password)
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return {"message": "Login exitoso"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        "access_token",
        path="/",
        secure=settings.COOKIE_SECURE,
        httponly=True,
        samesite=settings.COOKIE_SAMESITE,
    )
    return {"message": "Sesión cerrada"}


@router.get("/me", response_model=UserPublic)
def me(user: Usuario = Depends(get_current_active_user)):
    return UserPublic.model_validate(user)
