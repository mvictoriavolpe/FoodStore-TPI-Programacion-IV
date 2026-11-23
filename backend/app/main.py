"""HTTP configuration and domain routers for Food Store."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import create_all_tables
from app.modules.auth.router import router as auth_router
from app.modules.usuarios.router import router as usuarios_router
from app.modules.categorias.router import router as categorias_router
from app.modules.productos.router import router as productos_router
from app.modules.pedidos.router import router as pedidos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all_tables()
    yield


app = FastAPI(title="Food Store", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def cookie_origin_guard(request: Request, call_next):
    # CORS alone does not block simple cross-origin form submissions.
    origin = request.headers.get("origin")
    allowed_origins = {settings.FRONTEND_ORIGIN, str(request.base_url).rstrip("/")}
    if (
        request.method in {"POST", "PUT", "PATCH", "DELETE"}
        and origin
        and origin not in allowed_origins
    ):
        return JSONResponse(status_code=403, content={"detail": "Origen no autorizado"})
    response = await call_next(request)
    if request.url.path.startswith("/api/v1/auth"):
        response.headers["Cache-Control"] = "no-store"
    return response


for router in [
    auth_router,
    usuarios_router,
    categorias_router,
    productos_router,
    pedidos_router,
]:
    app.include_router(router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["health"])
def health():
    return {"ok": True}
