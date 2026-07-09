"""
Servidor HTTP (FastAPI) — expone la plataforma de torneos como API REST.
Punto de entrada alternativo a main.py (que sigue siendo la versión CLI).
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from app.exceptions import (
    UsuarioDuplicadoError,
    CredencialesInvalidasError,
    RepositorioError,
)
from app.repositories.usuario_repo import UsuarioRepository
from app.services.auth_service import AuthService

app = FastAPI(title="Canchalibre API", version="1.0.0")

# ── CORS: permite que el frontend (Vite, puerto 5173) le hable a esta API ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Inyección manual de dependencias (repo -> service) ──────────────────────
usuario_repo = UsuarioRepository()
auth_service = AuthService(usuario_repo)

security = HTTPBearer()


# ── Esquemas de entrada/salida (Pydantic) ───────────────────────────────────

class RegistroRequest(BaseModel):
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Dependencia: extrae y valida el usuario autenticado desde el token ─────

def obtener_usuario_actual(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        return auth_service.verificar_token(token)
    except CredencialesInvalidasError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


# ── Endpoints ────────────────────────────────────────────────────────────

@app.get("/")
def raiz():
    return {"mensaje": "Canchalibre API activa"}


@app.post("/auth/registro")
def registro(payload: RegistroRequest):
    try:
        usuario = auth_service.registrar(
            nombres=payload.nombres,
            apellido_paterno=payload.apellido_paterno,
            apellido_materno=payload.apellido_materno,
            email=payload.email,
            password=payload.password,
        )
        return {"mensaje": "Usuario registrado exitosamente.", "usuario": usuario}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except UsuarioDuplicadoError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/auth/login")
def login(payload: LoginRequest):
    try:
        resultado = auth_service.login(email=payload.email, password=payload.password)
        return resultado
    except CredencialesInvalidasError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/auth/yo")
def yo(usuario_actual: dict = Depends(obtener_usuario_actual)):
    """Retorna los datos del usuario autenticado según su token. Sirve para validar sesión."""
    return usuario_actual