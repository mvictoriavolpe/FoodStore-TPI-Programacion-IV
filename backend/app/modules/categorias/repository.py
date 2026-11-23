from sqlmodel import select
from app.core.base_repository import BaseRepository
from app.modules.categorias.models import Categoria


class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session):
        super().__init__(session, Categoria)

    def get_by_nombre(self, nombre):
        return self.session.exec(
            select(Categoria).where(Categoria.nombre == nombre)
        ).first()

    def list_active(self):
        return self.session.exec(
            select(Categoria).where(Categoria.activo == True).order_by(Categoria.id)
        ).all()
