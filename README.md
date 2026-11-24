# Food Store · UTN Programación 4

Aplicación web para un negocio de comidas. Permite registrarse, consultar el catálogo, armar un carrito, confirmar pedidos con entrega a domicilio y seguir su estado. El administrador gestiona categorías, productos, stock, pedidos y usuarios.

- **Repositorio público de GitHub:** https://github.com/mvictoriavolpe/FoodStore-TPI-Programacion-IV
- **Video demostrativo público (10–15 minutos):** https://youtu.be/-DrjK2S5mKo
- **Entrega indicada:** 24/11/2026 a las 23:59 (Argentina).

## Tecnologías

Backend: Python 3.11–3.13, FastAPI, SQLModel, PostgreSQL con psycopg2, SQLite para desarrollo, Pydantic Settings, JWT con python-jose y hash con `passlib[bcrypt]==1.7.4` / `bcrypt==4.0.1`.

Frontend: React 19, TypeScript 5.9 estricto sin `any`, Vite 7, Tailwind CSS 4, React Router 7, Axios, TanStack Query 5, TanStack Form 1, TanStack Table 8 y Zustand 5 con persistencia.

Las versiones directas están fijadas en `backend/requirements.txt` y `frontend/package.json`. `frontend/pnpm-lock.yaml` fija la resolución del frontend. Las ilustraciones SVG son locales y no requieren servicios de imágenes.

## Requisitos previos

- Python 3.11, 3.12 o 3.13. No usar Python 3.14 para este proyecto.
- Node.js 20.19+ dentro de la rama 20, o 22.12+ (incluye Node 24).
- pnpm 9 o superior; versión de referencia: 9.15.9.
- Para PostgreSQL: servidor 15 o superior y una base vacía creada previamente. SQLite funciona sin instalar un servidor.
- Dos terminales: una para el backend y otra para el frontend.

## Ejecución en Windows / PowerShell

Ubicarse en la carpeta raíz que contiene `backend/`, `frontend/` y este README.

### Backend

```powershell
cd backend
py -3.13 -m venv .venv
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m app.db.seed
.\.venv\Scripts\uvicorn.exe app.main:app --reload
```

Si se usa otra versión admitida, cambiar `-3.13` por `-3.11` o `-3.12`. Si `python --version` ya apunta al intérprete correcto, también se puede crear el entorno con `python -m venv .venv`. Los comandos anteriores no requieren habilitar scripts de activación de PowerShell.

API: http://localhost:8000/api/v1 · Swagger: http://localhost:8000/docs · ReDoc: http://localhost:8000/redoc · Salud: http://localhost:8000/api/v1/health.

El arranque y el seed crean las cinco tablas si no existen. La base SQLite se guarda en `backend/foodstore.db`; no forma parte del ZIP. Ejecutar siempre desde `backend/` para resolver `.env` y la ruta de la base correctamente.

### Frontend (otra terminal)

```powershell
cd frontend
Copy-Item .env.example .env
pnpm install
pnpm build
pnpm dev
```

Abrir **http://localhost:5173**. Mantener el backend iniciado. Vite debe usar el puerto 5173: si está ocupado, detener el proceso anterior o actualizar `FRONTEND_ORIGIN` para que coincida exactamente. Usar `localhost` en ambos servicios; mezclarlo con `127.0.0.1` cambia el origen y el ámbito de las cookies.

Para revisar la compilación de producción: `pnpm preview --port 5173` con el servidor de desarrollo detenido y el backend iniciado. En un hosting estático, configurar el fallback de rutas a `index.html` porque se usa BrowserRouter.

### Linux / macOS

```bash
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
cp .env.example .env
pip install -r requirements.txt
python -m app.db.seed
uvicorn app.main:app --reload
```

En otra terminal: `cd frontend`, `cp .env.example .env`, `pnpm install`, `pnpm build` y `pnpm dev`.

## Variables de entorno

`backend/.env.example` incluye:

| Variable | Valor para desarrollo / uso |
| --- | --- |
| `DATABASE_URL` | `sqlite:///./foodstore.db` |
| `SECRET_KEY` | Clave de firma de al menos 32 caracteres; reemplazar el ejemplo por un secreto propio |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `FRONTEND_ORIGIN` | `http://localhost:5173`; un origen exacto, sin barra final |
| `COOKIE_SECURE` | `false` en HTTP local; `true` al usar HTTPS |
| `COOKIE_SAMESITE` | `lax`; para frontend/backend en sitios diferentes usar `none` con HTTPS y `COOKIE_SECURE=true` |

Para generar una clave: `python -c "import secrets; print(secrets.token_urlsafe(48))"` usando el intérprete del entorno virtual. No publicar el `.env` real ni la clave generada.

Para PostgreSQL, establecer por ejemplo `DATABASE_URL=postgresql://foodstore:CLAVE@localhost:5432/foodstore_db`, crear esa base y ejecutar nuevamente el seed. El código y las dependencias incluyen el soporte; la verificación local se realizó con SQLite. No se verificó una instancia PostgreSQL en este entorno.

`frontend/.env.example`:

```dotenv
VITE_API_URL=http://localhost:8000/api/v1
```

Reiniciar los servidores después de cambiar variables. Las variables `VITE_*` son públicas: no colocar secretos en ellas.

## Datos iniciales y acceso

`python -m app.db.seed` es idempotente. Crea un administrador, tres categorías y nueve productos con stock 25 e imágenes locales. Repetirlo no duplica registros ni restablece el stock de productos existentes. Si encuentra productos del seed original sin imagen, completa únicamente esa imagen.

| Dato | Valor |
| --- | --- |
| Usuario administrador | `admin` |
| Contraseña inicial | `Admin1234!` |
| Rol | `admin` |

Ingresar en `/login`. El administrador accede a `/admin/resumen`; el cliente crea su cuenta en `/register`. Las credenciales anteriores son para la demostración académica.

## Arquitectura y comportamiento

```text
FoodStore/
├── backend/
│   ├── app/
│   │   ├── core/       # Configuración, seguridad, dependencias, repositorio y UoW base
│   │   ├── modules/
│   │   │   ├── auth/  # Router, Service y schemas; utiliza Usuario
│   │   │   ├── usuarios/
│   │   │   ├── categorias/
│   │   │   ├── productos/
│   │   │   └── pedidos/
│   │   ├── db/seed.py
│   │   └── main.py
│   ├── tests/
│   ├── scripts/package_delivery.py
│   └── requirements.txt
├── frontend/
│   ├── public/images/
│   └── src/
│       ├── features/   # auth, usuarios, categorias, productos y pedidos
│       ├── shared/     # Cliente HTTP, componentes, UI y layouts
│       ├── store/      # authStore y cartStore
│       └── routes/     # Rutas y control por sesión/rol
└── README.md
```

Cada módulo de dominio del backend tiene Router → Service → Unit of Work → Repository → Models y schemas de entrada/salida. Los Services abren `with self.uow as uow`; devuelven schemas dentro del bloque. Solo `UnitOfWork.__exit__` realiza commit o rollback y siempre cierra la sesión. Los routers traducen errores de dominio mediante `translate_errors` y no abren transacciones.

El JWT viaja únicamente en la cookie `access_token`, HttpOnly; nunca se devuelve como token en el cuerpo ni se guarda en localStorage. Zustand persiste solo el perfil de sesión y el carrito. Al montar la aplicación se confirma la sesión con `/auth/me`; el interceptor limpia los datos privados ante sesión vencida o cuenta desactivada. Los roles se verifican también en el backend.

- **RN-01:** pedido con al menos un ítem y sin productos repetidos; valida existencia, actividad, disponibilidad y stock, descuenta y crea las líneas dentro de una única transacción. Ante error se revierte todo.
- **RN-02:** `PENDIENTE → EN_PREPARACION | CANCELADO`; `EN_PREPARACION → ENTREGADO | CANCELADO`. Los estados entregado y cancelado son terminales.
- **RN-03:** la cancelación restituye stock en la misma transacción; no permite restituirlo dos veces.
- **RN-04:** el cliente consulta y cancela solo pedidos propios pendientes. El administrador consulta todos y gestiona estados desde el panel. No puede desactivar su propia cuenta.
- **RN-05:** las líneas copian nombre y precio; líneas y total quedan fijos. No hay edición ni borrado de pedidos.
- **RN-06:** pago en `EFECTIVO` o `TRANSFERENCIA` y dirección de 5 a 200 caracteres. El pago es manual; la aplicación registra la opción elegida y no procesa cobros.

PostgreSQL utiliza bloqueos de filas `SELECT FOR UPDATE`; SQLite serializa las operaciones con `BEGIN IMMEDIATE`. Los productos se bloquean en orden de ID. La cancelación restituye stock incluso si el producto fue dado de baja después de comprarlo.

Categorías y productos tienen baja lógica. Una categoría inactiva conserva su nombre único y **no oculta sus productos**; para retirarlos hay que darlos de baja por separado. PUT conserva los campos omitidos. Las activaciones/desactivaciones de usuarios son idempotentes. El resumen usa agregaciones SQL y cuenta los pedidos de hoy con fecha UTC.

## API

Todos los endpoints tienen prefijo `/api/v1`. Swagger contiene los schemas y las respuestas. Para usar Swagger, ejecutar `/auth/token` con formulario; el navegador conserva la cookie para las siguientes operaciones.

| Módulo | Endpoints |
| --- | --- |
| Auth | `POST /auth/register`, `POST /auth/token`, `POST /auth/logout`, `GET /auth/me` |
| Usuarios (admin) | `GET /admin/usuarios`, `POST /admin/usuarios/{id}/activar`, `POST /admin/usuarios/{id}/desactivar` |
| Categorías | `GET/POST /categorias`, `GET/PUT/DELETE /categorias/{id}` |
| Productos | `GET/POST /productos`, `GET/PUT/DELETE /productos/{id}`, `PATCH /productos/{id}/stock` |
| Pedidos | `GET/POST /pedidos`, `GET /pedidos/resumen`, `GET /pedidos/{id}`, `PATCH /pedidos/{id}/estado`, `PATCH /pedidos/{id}/cancelar` |

Las escrituras de catálogo y la gestión de estados requieren admin. Las lecturas de catálogo son públicas. Las listas paginadas reciben `skip=0`, `limit=20` (máximo 100), y devuelven `{total, items}`. Productos acepta `search`, `categoria_id` y `disponible`; pedidos acepta `estado`.

Códigos: 201 al registrar o crear, 204 sin cuerpo en bajas de catálogo, 401 sin sesión válida, 403 sin permiso o pedido ajeno, 404 inexistente/inactivo, 409 duplicado, 400 regla de negocio o cuenta desactivada, 422 datos inválidos.

## Pruebas y verificación

Pruebas automatizadas de API desde `backend/`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Cada prueba crea su propia base temporal. Cubren autenticación/cookies, permisos, activación de usuarios, catálogo, bajas lógicas, snapshots, rollback, estados, stock, CORS y operaciones simultáneas de compra/cancelación.

Prueba de integración en Chrome: instalar `requirements-e2e.txt`, tener Google Chrome y ejecutar `python tests/browser_smoke.py` desde `backend/`, con ambos servidores iniciados en localhost. **Usar una base de prueba recién creada**, porque el recorrido crea usuarios, categorías, productos y pedidos. Por ejemplo, en la terminal del backend antes de iniciar el servidor:

```powershell
New-Item -ItemType Directory -Force .qa | Out-Null
$qaStamp = Get-Date -Format 'yyyyMMddHHmmss'
$env:DATABASE_URL = "sqlite:///./.qa/browser-$qaStamp.db"
.\.venv\Scripts\python.exe -m app.db.seed
.\.venv\Scripts\uvicorn.exe app.main:app --reload
```

En otra terminal con la misma carpeta `backend/`: `.\.venv\Scripts\python.exe -m pip install -r requirements-e2e.txt` y `.\.venv\Scripts\python.exe tests/browser_smoke.py`. El script guarda capturas y resultado en `.qa/`, que se excluye del ZIP. Para volver a la base habitual, detener el servidor y quitar la variable de esa terminal con `Remove-Item Env:DATABASE_URL`.

Comprobaciones realizadas el 23/11/2026 con Python 3.13.2, Node 24.14.1, pnpm 9.15.9 y SQLite:

- Instalación de dependencias backend/frontend y `pip check`.
- Seed ejecutado repetidamente sin duplicados.
- Pruebas de API: **12 aprobadas**, incluidos acceso sin sesión y permisos del administrador al crear/cancelar pedidos.
- `pnpm build`: TypeScript y Vite completados.
- `uvicorn app.main:app --reload` y `pnpm dev`: ambos servidores iniciados.

- Chrome: **7 comprobaciones integrales aprobadas**, sin errores de JavaScript: catálogo, registro/login, carrito persistido, compra en efectivo/transferencia, detalle y cancelación con stock, administración y vista móvil de 390 px sin desborde horizontal.
- `/docs`, `/redoc`, `/openapi.json` y `/api/v1/health`: HTTP 200.

Las capturas y el resultado del navegador están en `backend/.qa/` durante la revisión local; se excluyen de la entrega. Pytest informa una advertencia de deprecación de Starlette/AnyIO que no impide las pruebas. PostgreSQL y un despliegue público requieren verificación en el entorno correspondiente.

## Preparación de entrega

Desde la raíz:

```powershell
.\backend\.venv\Scripts\python.exe backend/scripts/package_delivery.py
```

Genera `FoodStore_Entrega.zip`, con raíz `FoodStore/` y `backend/`, `frontend/`, `README.md`. Incluye los ejemplos `.env.example` y el lockfile. Excluye `node_modules`, entornos virtuales, `.env` reales, bases de datos, builds, cachés, archivos temporales, metadatos Git y videos. El generador comprueba la integridad del ZIP y las exclusiones.

