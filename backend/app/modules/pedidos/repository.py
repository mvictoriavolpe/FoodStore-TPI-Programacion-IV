from datetime import datetime, time, timedelta, timezone
from sqlalchemy import func
from sqlmodel import select
from app.core.base_repository import BaseRepository
from app.modules.pedidos.models import Pedido, DetallePedido


class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session):
        super().__init__(session, Pedido)

    def get_for_update(self, identifier):
        return self.session.exec(
            select(Pedido).where(Pedido.id == identifier).with_for_update()
        ).first()

    def list_by_usuario(self, usuario_id=None, skip=0, limit=20, estado=None):
        statement = select(Pedido)
        if usuario_id is not None:
            statement = statement.where(Pedido.usuario_id == usuario_id)
        if estado:
            statement = statement.where(Pedido.estado == estado)
        return self.page(statement.order_by(Pedido.id.desc()), skip, limit)

    def add_item(self, item: DetallePedido):
        self.session.add(item)
        self.session.flush()

    def count_by_estado(self, estado):
        return self.session.exec(
            select(func.count()).select_from(Pedido).where(Pedido.estado == estado)
        ).one()

    def summary(self):
        today = datetime.combine(
            datetime.now(timezone.utc).date(), time.min, tzinfo=timezone.utc
        )
        return {
            "pendientes": self.count_by_estado("PENDIENTE"),
            "en_preparacion": self.count_by_estado("EN_PREPARACION"),
            "entregados": self.count_by_estado("ENTREGADO"),
            "cancelados": self.count_by_estado("CANCELADO"),
            "pedidos_hoy": self.session.exec(
                select(func.count())
                .select_from(Pedido)
                .where(
                    Pedido.created_at >= today,
                    Pedido.created_at < today + timedelta(days=1),
                )
            ).one(),
            "ingresos_entregados": self.session.exec(
                select(func.coalesce(func.sum(Pedido.total), 0)).where(
                    Pedido.estado == "ENTREGADO"
                )
            ).one(),
        }
