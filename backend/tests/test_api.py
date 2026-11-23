from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from sqlmodel import Session, select

from app.main import app
from app.core.config import settings
from app.db.seed import seed
from app.modules.usuarios.models import Usuario
from app.modules.categorias.models import Categoria
from app.modules.productos.models import Producto
from app.modules.pedidos.models import Pedido, DetallePedido

API = "/api/v1"


def order_payload(*items, **extra):
    return {
        "items": [
            {"producto_id": identifier, "cantidad": quantity}
            for identifier, quantity in (items or [(1, 2)])
        ],
        "forma_pago": "EFECTIVO",
        "direccion_entrega": "San Martín 123",
        **extra,
    }


def stock(client, identifier=1):
    return client.get(f"{API}/productos/{identifier}").json()["stock"]


def test_seed_is_idempotent(clients):
    *_, engine = clients
    seed()
    seed()
    with Session(engine) as session:
        for model, expected in [(Usuario, 3), (Categoria, 3), (Producto, 9)]:
            assert (
                session.exec(select(func.count()).select_from(model)).one() == expected
            )
        assert all(
            p.imagen_url and p.stock > 0 for p in session.exec(select(Producto)).all()
        )


def test_auth_cookie_errors_and_roles(clients):
    customer, admin, _, _ = clients
    result = customer.post(
        f"{API}/auth/token", data={"username": "cliente", "password": "Cliente123!"}
    )
    assert result.json() == {"message": "Login exitoso"}
    cookie = result.headers["set-cookie"].lower()
    assert (
        "httponly" in cookie and "samesite=lax" in cookie and "max-age=1800" in cookie
    )
    assert "hashed_password" not in customer.get(f"{API}/auth/me").json()
    assert customer.get(f"{API}/admin/usuarios").status_code == 403
    assert customer.get(f"{API}/pedidos/resumen").status_code == 403
    assert (
        customer.post(f"{API}/categorias", json={"nombre": "Prueba"}).status_code == 403
    )
    assert (
        customer.post(
            f"{API}/auth/token", data={"username": "cliente", "password": "incorrecta"}
        ).status_code
        == 401
    )
    assert (
        customer.post(
            f"{API}/auth/register",
            json={
                "username": "cliente",
                "full_name": "Cliente",
                "email": "nuevo@example.com",
                "password": "Cliente123!",
            },
        ).status_code
        == 409
    )
    assert (
        customer.post(
            f"{API}/auth/register",
            json={
                "username": "nuevo",
                "full_name": "Cliente",
                "email": "cliente@example.com",
                "password": "Cliente123!",
            },
        ).status_code
        == 409
    )
    result = customer.post(
        f"{API}/auth/register",
        json={
            "username": "nuevo",
            "full_name": "Cliente",
            "email": "nuevo@example.com",
            "password": "Cliente123!",
            "role": "admin",
        },
    )
    assert result.status_code == 201 and result.json()["role"] == "user"
    assert admin.post(f"{API}/admin/usuarios/1/desactivar").status_code == 400
    assert customer.post(f"{API}/auth/logout").status_code == 200
    assert customer.get(f"{API}/auth/me").status_code == 401
    customer.cookies.set("access_token", "invalido")
    assert customer.get(f"{API}/auth/me").status_code == 401
    customer.cookies.clear()
    expired = jwt.encode(
        {"sub": "cliente", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    customer.cookies.set("access_token", expired)
    assert customer.get(f"{API}/auth/me").status_code == 401


def test_user_activation(clients):
    customer, admin, _, _ = clients
    identifier = customer.get(f"{API}/auth/me").json()["id"]
    for _ in range(2):
        assert (
            admin.post(f"{API}/admin/usuarios/{identifier}/desactivar").status_code
            == 200
        )
    assert (
        customer.get(f"{API}/auth/me").json()["detail"]
        == "Cuenta de usuario desactivada"
    )
    assert (
        customer.post(
            f"{API}/auth/token", data={"username": "cliente", "password": "Cliente123!"}
        ).status_code
        == 400
    )
    for _ in range(2):
        assert (
            admin.post(f"{API}/admin/usuarios/{identifier}/activar").status_code == 200
        )
    assert customer.get(f"{API}/auth/me").status_code == 200
    assert admin.post(f"{API}/admin/usuarios/9999/activar").status_code == 404


def test_catalog_crud_and_logical_delete(clients):
    customer, admin, _, _ = clients
    created = admin.post(
        f"{API}/categorias", json={"nombre": "Postres", "descripcion": "Dulces"}
    )
    assert created.status_code == 201
    category_id = created.json()["id"]
    assert (
        admin.post(f"{API}/categorias", json={"nombre": "Postres"}).status_code == 409
    )
    assert (
        admin.put(
            f"{API}/categorias/{category_id}", json={"descripcion": "Artesanales"}
        ).json()["nombre"]
        == "Postres"
    )
    assert (
        admin.put(
            f"{API}/categorias/{category_id}", json={"nombre": "Pizzas"}
        ).status_code
        == 409
    )
    result = admin.post(
        f"{API}/productos",
        json={
            "categoria_id": category_id,
            "nombre": "Brownie",
            "precio_base": 2500.5,
            "stock": 4,
        },
    )
    assert result.status_code == 201
    identifier = result.json()["id"]
    assert (
        admin.put(
            f"{API}/productos/{identifier}", json={"descripcion": "Con chocolate"}
        ).json()["stock"]
        == 4
    )
    assert (
        admin.patch(
            f"{API}/productos/{identifier}/stock",
            json={"stock": 10, "disponible": False},
        ).json()["stock"]
        == 10
    )
    result = customer.get(
        f"{API}/productos",
        params={
            "search": "BROWN",
            "categoria_id": category_id,
            "disponible": False,
            "limit": 1,
        },
    )
    assert result.json()["total"] == 1 and result.json()["items"][0]["id"] == identifier
    assert (
        customer.get(f"{API}/productos", params={"limit": 2, "skip": 2}).json()[
            "items"
        ][0]["id"]
        == 3
    )
    assert admin.delete(f"{API}/categorias/{category_id}").status_code == 204
    # Category deletion retains its unique name and does not hide existing products.
    assert customer.get(f"{API}/productos/{identifier}").status_code == 200
    assert (
        customer.get(f"{API}/productos/{identifier}").json()["categoria"]["activo"]
        is False
    )
    assert (
        admin.post(f"{API}/categorias", json={"nombre": "Postres"}).status_code == 409
    )
    assert (
        admin.post(
            f"{API}/productos",
            json={"categoria_id": category_id, "nombre": "Otro", "precio_base": 5},
        ).status_code
        == 404
    )
    assert (
        admin.put(f"{API}/productos/1", json={"categoria_id": category_id}).status_code
        == 404
    )
    for method, payload in [
        ("get", None),
        ("put", {"nombre": "Otro"}),
        ("delete", None),
    ]:
        assert (
            getattr(admin, method)(
                f"{API}/categorias/{category_id}",
                **({"json": payload} if payload else {}),
            ).status_code
            == 404
        )
    result = admin.delete(f"{API}/productos/{identifier}")
    assert result.status_code == 204 and result.content == b""
    assert admin.get(f"{API}/productos/{identifier}").status_code == 404
    assert (
        admin.put(f"{API}/productos/{identifier}", json={"nombre": "Otro"}).status_code
        == 404
    )
    assert (
        admin.patch(
            f"{API}/productos/{identifier}/stock", json={"stock": 1, "disponible": True}
        ).status_code
        == 404
    )
    assert admin.delete(f"{API}/productos/{identifier}").status_code == 404


def test_order_snapshots_owner_and_stock(clients):
    customer, admin, other, _ = clients
    before = stock(customer)
    response = customer.post(f"{API}/pedidos", json=order_payload())
    assert response.status_code == 201, response.text
    order = response.json()
    assert order["estado"] == "PENDIENTE" and stock(customer) == before - 2
    assert order["total"] == sum(item["subtotal"] for item in order["items"])
    assert other.get(f'{API}/pedidos/{order["id"]}').status_code == 403
    assert other.patch(f'{API}/pedidos/{order["id"]}/cancelar').status_code == 403
    assert other.get(f"{API}/pedidos").json()["total"] == 0
    assert (
        customer.patch(
            f'{API}/pedidos/{order["id"]}/estado', json={"estado": "ENTREGADO"}
        ).status_code
        == 403
    )
    assert admin.get(f"{API}/pedidos").json()["total"] == 1
    admin.put(f"{API}/productos/1", json={"nombre": "Renombrado", "precio_base": 99999})
    assert (
        customer.get(f'{API}/pedidos/{order["id"]}').json()["items"] == order["items"]
    )
    assert customer.patch(f'{API}/pedidos/{order["id"]}/cancelar').status_code == 200
    assert stock(customer) == before
    assert customer.patch(f'{API}/pedidos/{order["id"]}/cancelar').status_code == 400
    assert stock(customer) == before
    assert customer.get(f"{API}/pedidos/99999").status_code == 404


def test_atomic_rollback_and_business_errors(clients):
    customer, admin, _, engine = clients
    before = stock(customer)
    for items, code in [
        ([(1, 1), (2, 999)], 400),
        ([(1, 1), (99999, 1)], 404),
        ([(1, 1), (1, 2)], 400),
    ]:
        assert (
            customer.post(f"{API}/pedidos", json=order_payload(*items)).status_code
            == code
        )
        assert stock(customer) == before
        assert customer.get(f"{API}/pedidos").json()["total"] == 0
    with Session(engine) as session:
        assert session.exec(select(func.count()).select_from(DetallePedido)).one() == 0
    admin.patch(f"{API}/productos/1/stock", json={"stock": before, "disponible": False})
    assert customer.post(f"{API}/pedidos", json=order_payload()).status_code == 400
    admin.delete(f"{API}/productos/1")
    assert customer.post(f"{API}/pedidos", json=order_payload()).status_code == 404


def test_state_machine_summary_and_deleted_product_restore(clients):
    customer, admin, _, _ = clients
    order = customer.post(f"{API}/pedidos", json=order_payload()).json()
    url = f'{API}/pedidos/{order["id"]}'
    assert admin.patch(url + "/estado", json={"estado": "ENTREGADO"}).status_code == 400
    assert (
        admin.patch(url + "/estado", json={"estado": "EN_PREPARACION"}).status_code
        == 200
    )
    assert customer.patch(url + "/cancelar").status_code == 400
    assert admin.patch(url + "/estado", json={"estado": "ENTREGADO"}).status_code == 200
    assert admin.patch(url + "/estado", json={"estado": "CANCELADO"}).status_code == 400
    summary = admin.get(f"{API}/pedidos/resumen").json()
    assert (
        summary["entregados"] == 1 and summary["ingresos_entregados"] == order["total"]
    )
    assert summary["pedidos_hoy"] == 1
    second = customer.post(f"{API}/pedidos", json=order_payload()).json()
    url = f'{API}/pedidos/{second["id"]}'
    assert (
        admin.patch(url + "/estado", json={"estado": "EN_PREPARACION"}).status_code
        == 200
    )
    admin.delete(f"{API}/productos/1")
    assert admin.patch(url + "/estado", json={"estado": "CANCELADO"}).status_code == 200
    assert admin.get(f"{API}/pedidos/resumen").json()["cancelados"] == 1


def test_schema_validation_and_cors(clients):
    customer, admin, _, _ = clients
    for extra in [
        {"forma_pago": "TARJETA"},
        {"direccion_entrega": "123"},
        {"items": []},
        {"items": [{"producto_id": 1, "cantidad": 0}]},
    ]:
        assert (
            customer.post(f"{API}/pedidos", json=order_payload(**extra)).status_code
            == 422
        )
    for extra in [{"stock": -1}, {"precio_base": -1}, {"stock": None}]:
        assert admin.put(f"{API}/productos/1", json=extra).status_code == 422
    assert admin.put(f"{API}/categorias/1", json={"nombre": None}).status_code == 422
    assert customer.get(f"{API}/productos?limit=101").status_code == 422
    response = customer.options(
        f"{API}/pedidos",
        headers={
            "Origin": settings.FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.headers["access-control-allow-credentials"] == "true"
    assert response.headers["access-control-allow-origin"] == settings.FRONTEND_ORIGIN
    assert (
        customer.post(
            f"{API}/auth/logout", headers={"Origin": "https://untrusted.example"}
        ).status_code
        == 403
    )


def test_concurrent_last_unit_cannot_oversell(clients):
    customer, admin, _, _ = clients
    admin.patch(f"{API}/productos/1/stock", json={"stock": 1, "disponible": True})
    cookies = dict(customer.cookies)

    def purchase(_):
        with TestClient(app) as client:
            client.cookies.update(cookies)
            return client.post(f"{API}/pedidos", json=order_payload((1, 1))).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(purchase, range(2)))
    assert sorted(results) == [201, 400]
    assert stock(customer) == 0
    assert customer.get(f"{API}/pedidos").json()["total"] == 1


def test_concurrent_cancellation_restores_once(clients):
    customer, _, _, _ = clients
    before = stock(customer)
    order = customer.post(f"{API}/pedidos", json=order_payload()).json()
    cookies = dict(customer.cookies)

    def cancel(_):
        with TestClient(app) as client:
            client.cookies.update(cookies)
            return client.patch(f'{API}/pedidos/{order["id"]}/cancelar').status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(cancel, range(2)))
    assert sorted(results) == [200, 400]
    assert stock(customer) == before


def test_protected_endpoints_require_authentication(clients):
    with TestClient(app) as anonymous:
        operations = [
            ("get", "/auth/me", None),
            ("get", "/admin/usuarios", None),
            ("post", "/admin/usuarios/2/activar", None),
            ("post", "/admin/usuarios/2/desactivar", None),
            ("get", "/pedidos", None),
            ("get", "/pedidos/resumen", None),
            ("get", "/pedidos/1", None),
            ("post", "/pedidos", order_payload()),
            ("patch", "/pedidos/1/cancelar", None),
            ("patch", "/pedidos/1/estado", {"estado": "CANCELADO"}),
            ("post", "/categorias", {"nombre": "Prueba"}),
            ("put", "/categorias/1", {"nombre": "Prueba"}),
            ("delete", "/categorias/1", None),
            (
                "post",
                "/productos",
                {"nombre": "Prueba", "categoria_id": 1, "precio_base": 5},
            ),
            ("put", "/productos/1", {"nombre": "Prueba"}),
            ("patch", "/productos/1/stock", {"stock": 1, "disponible": True}),
            ("delete", "/productos/1", None),
        ]
        for method, path, payload in operations:
            response = getattr(anonymous, method)(
                API + path, **({"json": payload} if payload is not None else {})
            )
            assert response.status_code == 401, (method, path, response.text)
        assert anonymous.get(f"{API}/categorias").status_code == 200
        assert anonymous.get(f"{API}/productos").status_code == 200


def test_admin_order_permissions(clients):
    customer, admin, _, _ = clients
    own = admin.post(f"{API}/pedidos", json=order_payload((1, 1)))
    assert own.status_code == 201
    assert admin.patch(f'{API}/pedidos/{own.json()["id"]}/cancelar').status_code == 200
    client_order = customer.post(f"{API}/pedidos", json=order_payload((1, 1))).json()
    # The owner-cancellation endpoint remains owner-only, even for an admin.
    assert (
        admin.patch(f'{API}/pedidos/{client_order["id"]}/cancelar').status_code == 403
    )
    assert (
        admin.patch(
            f'{API}/pedidos/{client_order["id"]}/estado', json={"estado": "CANCELADO"}
        ).status_code
        == 200
    )
