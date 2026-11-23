from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from app.core.errors import DomainError, NotFound, Forbidden
from app.modules.pedidos.models import Pedido, DetallePedido
from app.modules.pedidos.schemas import PedidoRead, PedidosPaginados, ResumenPedidos
from app.modules.pedidos.unit_of_work import PedidoUnitOfWork

TRANSITIONS = {
    "PENDIENTE": {"EN_PREPARACION", "CANCELADO"},
    "EN_PREPARACION": {"ENTREGADO", "CANCELADO"},
    "ENTREGADO": set(),
    "CANCELADO": set(),
}


class PedidoNoEncontrado(NotFound):
    pass


class ProductoNoEncontrado(NotFound):
    pass


class PedidoAjeno(Forbidden):
    pass


class StockInsuficiente(DomainError):
    pass


class ProductoNoDisponible(DomainError):
    pass


class ProductoRepetido(DomainError):
    pass


class TransicionInvalida(DomainError):
    pass


class PedidoService:
    def __init__(self, uow=None):
        self.uow = uow or PedidoUnitOfWork()

    def create(self, data, user):
        with self.uow as uow:
            if not data.items:
                raise DomainError("El pedido debe tener al menos un ítem")
            ids = [item.producto_id for item in data.items]
            if len(ids) != len(set(ids)):
                raise ProductoRepetido("Producto repetido")
            if (
                data.forma_pago not in {"EFECTIVO", "TRANSFERENCIA"}
                or not 5 <= len(data.direccion_entrega.strip()) <= 200
            ):
                raise DomainError("Forma de pago o dirección inválida")
            order = Pedido(
                usuario_id=user.id,
                estado="PENDIENTE",
                forma_pago=data.forma_pago,
                direccion_entrega=data.direccion_entrega,
                notas=data.notas,
                total=0,
            )
            uow.pedidos.add(order)
            total = Decimal("0")
            # Lock in a stable order to prevent overlapping baskets from deadlocking.
            for item in sorted(data.items, key=lambda item: item.producto_id):
                product = uow.productos.get_for_update(item.producto_id)
                if not product or not product.activo:
                    raise ProductoNoEncontrado("Producto inexistente")
                if not product.disponible:
                    raise ProductoNoDisponible(
                        f"{product.nombre}: producto no disponible"
                    )
                if item.cantidad < 1:
                    raise DomainError("La cantidad debe ser mayor o igual a uno")
                if product.stock < item.cantidad:
                    raise StockInsuficiente(
                        f"{product.nombre}: stock insuficiente (disponible: {product.stock})"
                    )
                product.stock -= item.cantidad
                uow.productos.add(product)
                subtotal = (Decimal(str(product.precio_base)) * item.cantidad).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                uow.pedidos.add_item(
                    DetallePedido(
                        pedido_id=order.id,
                        producto_id=product.id,
                        nombre_producto=product.nombre,
                        precio_unitario=product.precio_base,
                        cantidad=item.cantidad,
                        subtotal=float(subtotal),
                    )
                )
                total += subtotal
            order.total = float(total)
            uow.pedidos.add(order)
            return PedidoRead.model_validate(order)

    def list(self, user, **filters):
        with self.uow as uow:
            total, orders = uow.pedidos.list_by_usuario(
                usuario_id=None if user.role == "admin" else user.id, **filters
            )
            return PedidosPaginados(
                total=total, items=[PedidoRead.model_validate(p) for p in orders]
            )

    def _get(self, repository, identifier, user, lock=False):
        order = (
            repository.get_for_update(identifier)
            if lock
            else repository.get_by_id(identifier)
        )
        if not order:
            raise PedidoNoEncontrado("Pedido inexistente")
        if order.usuario_id != user.id and user.role != "admin":
            raise PedidoAjeno("Pedido ajeno")
        return order

    def get(self, identifier, user):
        with self.uow as uow:
            return PedidoRead.model_validate(self._get(uow.pedidos, identifier, user))

    def change_state(self, identifier, state, user, own=False):
        with self.uow as uow:
            order = self._get(uow.pedidos, identifier, user, lock=True)
            if own:
                if order.usuario_id != user.id:
                    raise PedidoAjeno(
                        "Pedido ajeno; usá la gestión de estados para administrar otros pedidos"
                    )
                if order.estado != "PENDIENTE":
                    raise TransicionInvalida("Solo se cancela en PENDIENTE")
                state = "CANCELADO"
            elif user.role != "admin":
                raise Forbidden("No autorizado")
            if state not in TRANSITIONS.get(order.estado, set()):
                raise TransicionInvalida("Transición inválida")
            if state == "CANCELADO":
                for item in sorted(order.items, key=lambda item: item.producto_id):
                    # Logical deletion does not prevent restoring a product's stock.
                    product = uow.productos.get_for_update(item.producto_id)
                    if product is None:
                        raise ProductoNoEncontrado(
                            "No se pudo restituir el stock del producto"
                        )
                    product.stock += item.cantidad
                    uow.productos.add(product)
            order.estado = state
            order.updated_at = datetime.now(timezone.utc)
            uow.pedidos.add(order)
            return PedidoRead.model_validate(order)

    def summary(self):
        with self.uow as uow:
            return ResumenPedidos(**uow.pedidos.summary())
