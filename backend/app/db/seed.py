"""Idempotent demo data. Run from backend: python -m app.db.seed."""

from app.core.database import create_all_tables
from app.core.security import hash_password
from app.core.unit_of_work import UnitOfWork
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.categorias.models import Categoria
from app.modules.categorias.repository import CategoriaRepository
from app.modules.productos.models import Producto
from app.modules.productos.repository import ProductoRepository
from sqlmodel import select

DATA = {
    "Hamburguesas": [
        (
            "Clásica",
            8500,
            "Carne a la plancha, lechuga, tomate y nuestra salsa de la casa.",
            "burger",
        ),
        (
            "Doble queso",
            11200,
            "Dos medallones, doble cheddar y cebolla caramelizada.",
            "burger",
        ),
        (
            "Veggie",
            9200,
            "Medallón de garbanzos, palta, rúcula y mayonesa de limón.",
            "veggie",
        ),
    ],
    "Pizzas": [
        (
            "Muzzarella",
            14500,
            "Masa artesanal, salsa de tomates y abundante muzzarella.",
            "pizza",
        ),
        ("Napolitana", 16300, "Muzzarella, tomates frescos, ajo y albahaca.", "pizza"),
        (
            "Fugazzeta",
            16800,
            "Muzzarella y cebolla dorada sobre nuestra masa artesanal.",
            "pizza",
        ),
    ],
    "Bebidas": [
        (
            "Limonada",
            3800,
            "Limón exprimido, menta fresca y un toque de jengibre.",
            "lemonade",
        ),
        ("Gaseosa", 3200, "Bien fría, ideal para acompañar tu pedido. 500 ml.", "soda"),
        ("Agua mineral", 2500, "Agua mineral sin gas. Botella de 500 ml.", "water"),
    ],
}


def seed():
    create_all_tables()
    with UnitOfWork() as uow:
        users = UsuarioRepository(uow.session)
        categories = CategoriaRepository(uow.session)
        products = ProductoRepository(uow.session)
        if not users.get_by_username("admin"):
            users.add(
                Usuario(
                    username="admin",
                    full_name="Administrador",
                    email="admin@foodstore.local",
                    hashed_password=hash_password("Admin1234!"),
                    role="admin",
                )
            )
        for name, items in DATA.items():
            category = categories.get_by_nombre(name)
            if category is None:
                category = categories.add(
                    Categoria(nombre=name, descripcion=f"Menú de {name}")
                )
            for title, price, description, image in items:
                existing = uow.session.exec(
                    select(Producto).where(
                        Producto.nombre == title, Producto.categoria_id == category.id
                    )
                ).first()
                if existing is None:
                    products.add(
                        Producto(
                            categoria_id=category.id,
                            nombre=title,
                            descripcion=description,
                            precio_base=price,
                            stock=25,
                            imagen_url=f"/images/{image}.svg",
                        )
                    )
                elif not existing.imagen_url:
                    # Upgrade the original seed without touching price, stock or status.
                    existing.imagen_url = f"/images/{image}.svg"
                    products.add(existing)
    print("Seed idempotente completado: admin, tres categorías y nueve productos.")


if __name__ == "__main__":
    seed()
