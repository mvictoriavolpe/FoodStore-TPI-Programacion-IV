from sqlmodel import select
from app.core.base_repository import BaseRepository
from app.modules.productos.models import Producto


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session):
        super().__init__(session, Producto)

    def get_for_update(self, identifier):
        return self.session.exec(
            select(Producto).where(Producto.id == identifier).with_for_update()
        ).first()

    def search(self, skip=0, limit=20, search=None, categoria_id=None, disponible=None):
        statement = select(Producto).where(Producto.activo == True)
        if search:
            # Treat search as text, including literal % and _ characters.
            statement = statement.where(
                Producto.nombre.icontains(search, autoescape=True)
            )
        if categoria_id is not None:
            statement = statement.where(Producto.categoria_id == categoria_id)
        if disponible is not None:
            statement = statement.where(Producto.disponible == disponible)
        return self.page(statement.order_by(Producto.id), skip, limit)
