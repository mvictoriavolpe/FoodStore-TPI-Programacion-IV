from app.core.unit_of_work import UnitOfWork
from app.modules.categorias.repository import CategoriaRepository


class CategoriaUnitOfWork(UnitOfWork):
    def setup_repositories(self):
        self.categorias = CategoriaRepository(self.session)
