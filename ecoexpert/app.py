from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .engine import evaluar, REGLAS
from .models import Consulta

STATIC = Path(__file__).parent / "static"
app = FastAPI(title="EcoExpert básico", version="basico-1", docs_url=None, redoc_url=None, openapi_url=None)


@app.middleware("http")
async def headers(request: Request, call_next):
    try:
        if int(request.headers.get("content-length", "0")) > 16384:
            return JSONResponse({"detail": "Consulta demasiado grande."}, status_code=413)
    except ValueError:
        return JSONResponse({"detail": "Consulta inválida."}, status_code=400)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; frame-ancestors 'self'; base-uri 'self'"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/healthz")
def health():
    return {"status": "ok", "version": "basico-1", "rules": len(REGLAS)}


@app.post("/api/evaluate")
def consulta(datos: Consulta):
    return evaluar(datos)


@app.get("/api/rules")
def reglas():
    return REGLAS


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
