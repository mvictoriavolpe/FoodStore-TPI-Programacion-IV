from sqlalchemy import event
from sqlmodel import SQLModel, Session, create_engine

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=(
        {"check_same_thread": False, "timeout": 30}
        if settings.DATABASE_URL.startswith("sqlite")
        else {}
    ),
    pool_pre_ping=True,
)

if engine.dialect.name == "sqlite":

    @event.listens_for(engine, "connect")
    def sqlite_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")


def session_factory():
    return Session(engine, expire_on_commit=False)


def create_all_tables():
    # Register all five tables before creating metadata or configuring relationships.
    from app.modules.usuarios.models import Usuario  # noqa: F401
    from app.modules.categorias.models import Categoria  # noqa: F401
    from app.modules.productos.models import Producto  # noqa: F401
    from app.modules.pedidos.models import Pedido, DetallePedido  # noqa: F401

    SQLModel.metadata.create_all(engine)
