"""Real-browser integration check against running localhost backend and frontend.

Use an isolated database for this check (see README). Chrome is required.
Run from backend: python tests/browser_smoke.py
"""

import json
from pathlib import Path
from uuid import uuid4

from playwright.sync_api import sync_playwright, expect

SITE = "http://localhost:5173"
API = "http://localhost:8000/api/v1"


def main():
    output = Path(".qa")
    output.mkdir(exist_ok=True)
    username = f"prueba_{uuid4().hex[:8]}"
    errors = []
    checks = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("dialog", lambda dialog: dialog.accept())

        def navigate(path):
            page.goto(SITE + path)

        def api_product(identifier=1):
            response = context.request.get(f"{API}/productos/{identifier}")
            assert response.status == 200
            return response.json()

        def logout():
            page.get_by_role("button", name="Cerrar sesión", exact=True).click()
            expect(page).to_have_url(SITE + "/login")

        def login(name, password):
            page.get_by_label("Usuario", exact=True).fill(name)
            page.get_by_label("Contraseña", exact=True).fill(password)
            page.get_by_role("button", name="Ingresar", exact=True).click()

        def buy(payment="EFECTIVO"):
            navigate("/")
            page.get_by_role(
                "button", name="Agregar Clásica al carrito", exact=True
            ).click()
            navigate("/carrito")
            page.get_by_role("link", name="Continuar al checkout").click()
            page.get_by_label("Dirección de entrega").fill("San Martín 123, piso 2")
            page.get_by_label("Forma de pago").select_option(payment)
            with page.expect_response(
                lambda response: response.url == API + "/pedidos"
                and response.request.method == "POST"
            ) as result:
                page.get_by_role("button", name="Realizar pedido", exact=True).click()
            assert result.value.status == 201, result.value.text()
            expect(page).to_have_url(SITE + "/mis-pedidos")
            return result.value.json()

        navigate("/")
        expect(page.locator(".product-card")).to_have_count(6)
        assert page.locator(".product-image img").evaluate_all(
            "(images) => images.every(image => image.complete && image.naturalWidth > 0)"
        )
        page.screenshot(path=str(output / "catalogo-desktop.png"), full_page=True)
        page.get_by_role("button", name="Bebidas", exact=True).click()
        expect(page.locator(".product-card")).to_have_count(3)
        page.get_by_role("searchbox").fill("Limonada")
        expect(page.locator(".product-card")).to_have_count(1)
        page.get_by_role("searchbox").fill("producto inexistente")
        expect(
            page.get_by_text("No encontramos ese antojo. Probá otra búsqueda.")
        ).to_be_visible()
        page.get_by_role("searchbox").fill("")
        page.get_by_role("button", name="Todo el menú").click()
        expect(page.locator(".product-card")).to_have_count(6)
        page.get_by_role("button", name="Siguiente", exact=True).click()
        expect(page.locator(".product-card")).to_have_count(3)
        checks.append("Catálogo: imágenes, búsqueda, filtros, vacío y paginación")

        navigate("/register")
        page.get_by_label("Nombre completo", exact=True).fill("Cliente de prueba")
        page.get_by_label("Usuario", exact=True).fill(username)
        page.get_by_label("Email", exact=True).fill(f"{username}@example.com")
        page.get_by_label("Contraseña", exact=True).fill("Cliente123!")
        page.get_by_role("button", name="Crear cuenta", exact=True).click()
        expect(page).to_have_url(SITE + "/login")
        login(username, "Cliente123!")
        expect(page).to_have_url(SITE + "/")
        before = api_product()["stock"]
        page.get_by_role(
            "button", name="Agregar Clásica al carrito", exact=True
        ).click()
        navigate("/carrito")
        page.get_by_label("Cantidad de Clásica").fill("2")
        page.reload()
        expect(page.get_by_label("Cantidad de Clásica")).to_have_value("2")
        page.get_by_role("link", name="Continuar al checkout").click()
        page.get_by_label("Dirección de entrega").fill("San Martín 123, piso 2")
        with page.expect_response(
            lambda response: response.url == API + "/pedidos"
            and response.request.method == "POST"
        ) as result:
            page.get_by_role("button", name="Realizar pedido", exact=True).click()
        assert result.value.status == 201, result.value.text()
        first = result.value.json()
        expect(page).to_have_url(SITE + "/mis-pedidos")
        assert api_product()["stock"] == before - 2
        page.get_by_role("button", name="Ver detalle", exact=True).first.click()
        expect(page.get_by_role("dialog")).to_contain_text("San Martín 123")
        page.get_by_role("button", name="Cerrar", exact=True).click()
        page.get_by_role("button", name="Cancelar pedido", exact=True).first.click()
        expect(
            page.locator(".order-card")
            .filter(has_text=f'Pedido #{first["id"]}')
            .locator(".badge")
        ).to_have_text("Cancelado")
        assert api_product()["stock"] == before
        checks.append(
            "Registro, login, carrito persistido, checkout, detalle y cancelación con restitución"
        )

        second = buy("TRANSFERENCIA")
        assert second["forma_pago"] == "TRANSFERENCIA"
        assert api_product()["stock"] == before - 1
        navigate("/admin/productos")
        expect(page).to_have_url(SITE + "/unauthorized")
        checks.append("Pago por transferencia y restricción de rutas por rol")
        logout()
        login("admin", "Admin1234!")
        expect(page).to_have_url(SITE + "/admin/resumen")
        expect(page.locator(".metric")).to_have_count(6)

        navigate("/admin/categorias")
        page.get_by_label("Nombre", exact=True).fill("Postres de prueba")
        page.get_by_label("Descripción", exact=True).fill("Artesanales")
        page.get_by_role("button", name="Crear categoría", exact=True).click()
        expect(
            page.get_by_role("cell", name="Postres de prueba", exact=True)
        ).to_be_visible()
        row = page.get_by_role("row").filter(has_text="Postres de prueba")
        row.get_by_role("button", name="Editar", exact=True).click()
        page.get_by_label("Nombre", exact=True).fill("Postres editados")
        page.get_by_role("button", name="Guardar cambios", exact=True).click()
        expect(
            page.get_by_role("cell", name="Postres editados", exact=True)
        ).to_be_visible()

        navigate("/admin/productos")
        page.get_by_label("Nombre", exact=True).fill("Brownie de prueba")
        page.get_by_label("Categoría", exact=True).select_option(
            label="Postres editados"
        )
        page.get_by_label("Precio base (ARS)", exact=True).fill("2500.50")
        page.get_by_label("Stock", exact=True).fill("5")
        page.get_by_label("Descripción", exact=True).fill("Chocolate")
        page.get_by_role("button", name="Crear producto", exact=True).click()
        expect(page.get_by_text("Producto creado.", exact=True)).to_be_visible()
        page.get_by_role("button", name="Siguiente", exact=True).click()
        row = page.get_by_role("row").filter(has_text="Brownie de prueba")
        expect(row).to_be_visible()
        row.get_by_role("button", name="Stock", exact=True).click()
        page.get_by_label("Nuevo stock", exact=True).fill("8")
        page.get_by_role("button", name="Actualizar stock", exact=True).click()
        expect(page.get_by_role("dialog")).not_to_be_visible()
        # TanStack Table resets its client page after data changes.
        page.get_by_role("button", name="Siguiente", exact=True).click()
        row = page.get_by_role("row").filter(has_text="Brownie de prueba")
        expect(row.get_by_role("cell", name="8", exact=True)).to_be_visible()
        row.get_by_role("button", name="Sí", exact=True).click()
        page.get_by_role("button", name="Siguiente", exact=True).click()
        row = page.get_by_role("row").filter(has_text="Brownie de prueba")
        expect(row.get_by_role("button", name="No", exact=True)).to_be_visible()
        row.get_by_role("button", name="Editar", exact=True).click()
        page.get_by_label("Nombre", exact=True).fill("Brownie editado")
        page.get_by_role("button", name="Guardar cambios", exact=True).click()
        expect(page.get_by_text("Producto actualizado.", exact=True)).to_be_visible()
        page.get_by_role("button", name="Siguiente", exact=True).click()
        page.get_by_role("row").filter(has_text="Brownie editado").get_by_role(
            "button", name="Dar de baja", exact=True
        ).click()
        expect(page.get_by_text("Brownie editado", exact=True)).not_to_be_visible()
        navigate("/admin/categorias")
        page.get_by_role("row").filter(has_text="Postres editados").get_by_role(
            "button", name="Dar de baja", exact=True
        ).click()
        expect(
            page.get_by_role("cell", name="Postres editados", exact=True)
        ).not_to_be_visible()
        checks.append(
            "Administración: alta, edición y baja de categorías/productos, stock y disponibilidad"
        )

        navigate("/admin/pedidos")
        row = page.get_by_role("row").filter(
            has=page.get_by_role("button", name=f'#{second["id"]}', exact=True)
        )
        row.get_by_role("button", name="Preparar", exact=True).click()
        expect(row.locator(".badge")).to_have_text("En preparación")
        row.get_by_role("button", name="Cancelar", exact=True).click()
        expect(row.locator(".badge")).to_have_text("Cancelado")
        assert api_product()["stock"] == before
        checks.append(
            "Administrador: preparación y cancelación con restitución de stock"
        )

        navigate("/admin/usuarios")
        row = page.get_by_role("row").filter(
            has=page.get_by_role("cell", name=username, exact=True)
        )
        row.get_by_role("button", name="Desactivar", exact=True).click()
        expect(row.locator(".badge")).to_have_text("Desactivado")
        row.get_by_role("button", name="Activar", exact=True).click()
        expect(row.locator(".badge")).to_have_text("Activo")
        checks.append("Administración: activación y desactivación de usuarios")

        navigate("/")
        expect(page.locator(".product-card")).to_have_count(6)
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=str(output / "catalogo-mobile.png"), full_page=True)
        assert page.evaluate(
            "document.documentElement.scrollWidth <= window.innerWidth"
        ), "Hay desborde horizontal en móvil"
        page.get_by_role("button", name="Menú", exact=True).click()
        expect(
            page.get_by_role("link", name="Administración", exact=True)
        ).to_be_visible()
        assert not errors, errors
        checks.append("Vista móvil sin desborde y sin errores de JavaScript")
        browser.close()

    report = {"checks": checks, "javascript_errors": errors, "passed": len(checks)}
    (output / "browser-result.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
