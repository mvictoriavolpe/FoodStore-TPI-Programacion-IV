from app.core.errors import Conflict, NotFound, DomainError
from app.modules.categorias.models import Categoria
from app.modules.categorias.schemas import CategoriaRead
from app.modules.categorias.unit_of_work import CategoriaUnitOfWork


class CategoriaNoEncontrada(NotFound):
    pass


class NombreDuplicado(Conflict):
    pass


def require_category(repository, identifier):
    category = repository.get_by_id(identifier)
    if not category or not category.activo:
        raise CategoriaNoEncontrada("Categoría inexistente")
    return category


class CategoriaService:
    def __init__(self, uow=None):
        self.uow = uow or CategoriaUnitOfWork()

    def list(self):
        with self.uow as uow:
            return [
                CategoriaRead.model_validate(c) for c in uow.categorias.list_active()
            ]

    def get(self, identifier):
        with self.uow as uow:
            return CategoriaRead.model_validate(
                require_category(uow.categorias, identifier)
            )

    def save(self, data, identifier=None):
        with self.uow as uow:
            category = (
                require_category(uow.categorias, identifier)
                if identifier is not None
                else Categoria()
            )
            values = data.model_dump(exclude_unset=True)
            if "nombre" in values:
                name = values["nombre"]
                if name is None or not 2 <= len(name.strip()) <= 100:
                    raise DomainError("El nombre debe tener entre 2 y 100 caracteres")
                other = uow.categorias.get_by_nombre(name)
                if other and other.id != category.id:
                    raise NombreDuplicado("Nombre duplicado")
            for key, value in values.items():
                if value is None:
                    raise DomainError(f"{key} no admite null")
                setattr(category, key, value)
            uow.categorias.add(category)
            return CategoriaRead.model_validate(category)

    def delete(self, identifier):
        with self.uow as uow:
            category = require_category(uow.categorias, identifier)
            category.activo = False
            uow.categorias.add(category)
