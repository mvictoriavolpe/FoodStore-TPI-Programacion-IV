from math import isfinite
from app.core.errors import NotFound, DomainError
from app.modules.productos.models import Producto
from app.modules.productos.schemas import ProductoRead, ProductosPaginados
from app.modules.productos.unit_of_work import ProductoUnitOfWork


class ProductoNoEncontrado(NotFound):
    pass


def require_product(repository, identifier, lock=False):
    product = (
        repository.get_for_update(identifier)
        if lock
        else repository.get_by_id(identifier)
    )
    if not product or not product.activo:
        raise ProductoNoEncontrado("Producto inexistente")
    return product


class ProductoService:
    def __init__(self, uow=None):
        self.uow = uow or ProductoUnitOfWork()

    def list(self, **filters):
        with self.uow as uow:
            total, products = uow.productos.search(**filters)
            return ProductosPaginados(
                total=total, items=[ProductoRead.model_validate(p) for p in products]
            )

    def get(self, identifier):
        with self.uow as uow:
            return ProductoRead.model_validate(
                require_product(uow.productos, identifier)
            )

    def save(self, data, identifier=None):
        with self.uow as uow:
            product = (
                require_product(uow.productos, identifier, lock=True)
                if identifier is not None
                else Producto()
            )
            values = data.model_dump(exclude_unset=True)
            for key, value in values.items():
                if value is None:
                    raise DomainError(f"{key} no admite null")
            if "categoria_id" in values:
                category = uow.categorias.get_by_id(values["categoria_id"])
                if not category or not category.activo:
                    # Domain error is local; no dependency on another Service.
                    raise ProductoCategoriaNoEncontrada("Categoría inexistente")
            if "nombre" in values and not values["nombre"].strip():
                raise DomainError("El nombre es obligatorio")
            if "precio_base" in values and (
                not isfinite(values["precio_base"]) or values["precio_base"] < 0
            ):
                raise DomainError("El precio debe ser mayor o igual a cero")
            if "stock" in values and values["stock"] < 0:
                raise DomainError("El stock debe ser mayor o igual a cero")
            for key, value in values.items():
                setattr(product, key, value)
            uow.productos.add(product)
            return ProductoRead.model_validate(product)

    def delete(self, identifier):
        with self.uow as uow:
            product = require_product(uow.productos, identifier, lock=True)
            product.activo = False
            uow.productos.add(product)


class ProductoCategoriaNoEncontrada(NotFound):
    pass
