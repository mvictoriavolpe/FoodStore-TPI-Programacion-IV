from app.core.unit_of_work import UnitOfWork
from app.modules.productos.repository import ProductoRepository
from app.modules.categorias.repository import CategoriaRepository


class ProductoUnitOfWork(UnitOfWork):
    def setup_repositories(self):
        self.productos = ProductoRepository(self.session)
        self.categorias = CategoriaRepository(self.session)
