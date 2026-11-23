from contextlib import contextmanager

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


class DomainError(Exception):
    status_code = 400


class NotFound(DomainError):
    status_code = 404


class Conflict(DomainError):
    status_code = 409


class Forbidden(DomainError):
    status_code = 403


@contextmanager
def translate_errors():
    """Used by routers, keeping HTTP concerns outside business services."""
    try:
        yield
    except DomainError as error:
        raise HTTPException(error.status_code, str(error)) from error
    except IntegrityError as error:
        raise HTTPException(
            409, "Los datos entran en conflicto con un registro existente"
        ) from error
