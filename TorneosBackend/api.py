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

from datetime import date
import unicodedata

from app.exceptions import (
    UsuarioDuplicadoError,
    CredencialesInvalidasError,
    RepositorioError,
    TorneoNoEncontradoError,
    EquipoDuplicadoError,
    JugadorDuplicadoError,
)
from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.torneo_repo import TorneoRepository
from app.services.auth_service import AuthService
from app.services.torneo_service import TorneoService

from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.torneo_repo import TorneoRepository
from app.repositories.equipo_repo import EquipoRepository
from app.repositories.jugador_repo import JugadorRepository
from app.services.auth_service import AuthService
from app.services.torneo_service import TorneoService
from app.services.inscripcion_service import InscripcionService

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
torneo_repo = TorneoRepository()
torneo_service = TorneoService(torneo_repo)
equipo_repo = EquipoRepository()
jugador_repo = JugadorRepository()
inscripcion_service = InscripcionService(equipo_repo, torneo_repo, jugador_repo)
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


class TorneoCreateRequest(BaseModel):
    tipo_deporte: str        # 'futbol' o 'voley'
    nombre_torneo: str
    numero_equipos: int
    fecha_inicio: date


class EquipoCreateRequest(BaseModel):
    nombre_equipo: str
    numero_jugadores: int

class JugadorCreateRequest(BaseModel):
    nombre_jugador: str
    apellido_paterno: str
    apellido_materno: str
    dni: str

# ── Dependencia: extrae y valida el usuario autenticado desde el token ─────

def obtener_usuario_actual(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        return auth_service.verificar_token(token)
    except CredencialesInvalidasError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


def _quitar_tildes(texto: str) -> str:
    """Normaliza texto quitando tildes, para comparar 'Vóley' con 'voley'."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()


def _resolver_id_deporte(tipo_deporte: str) -> int:
    """
    Busca en la tabla Deporte el id_deporte correspondiente a 'futbol' o 'voley',
    para que el frontend no necesite conocer los IDs numéricos de la BD.
    """
    tipo_normalizado = _quitar_tildes(tipo_deporte.strip())
    deportes = torneo_service.listar_deportes()
    for deporte in deportes:
        if _quitar_tildes(deporte['nombre_deporte']).startswith(tipo_normalizado):
            return deporte['id_deporte']
    raise ValueError(f"No se encontró el deporte '{tipo_deporte}' en la base de datos.")

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


@app.get("/torneos/deportes")
def listar_deportes_endpoint():
    try:
        return torneo_service.listar_deportes()
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/torneos")
def crear_torneo_endpoint(
    payload: TorneoCreateRequest,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        id_deporte = _resolver_id_deporte(payload.tipo_deporte)
        torneo = torneo_service.crear_torneo(
            tipo_deporte=payload.tipo_deporte,
            nombre_torneo=payload.nombre_torneo,
            numero_equipos=payload.numero_equipos,
            fecha_inicio=payload.fecha_inicio,
            id_deporte=id_deporte,
        )
        return {"mensaje": "Torneo creado exitosamente.", "torneo": torneo}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/torneos")
def listar_torneos_endpoint():
    try:
        return torneo_service.listar_torneos()
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/torneos/{id_torneo}")
def obtener_torneo_endpoint(id_torneo: int):
    try:
        return torneo_service.obtener_torneo(id_torneo)
    except TorneoNoEncontradoError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/torneos/{id_torneo}/equipos")
def inscribir_equipo_endpoint(
    id_torneo: int,
    payload: EquipoCreateRequest,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        equipo = inscripcion_service.inscribir_equipo(
            nombre_equipo=payload.nombre_equipo,
            numero_jugadores=payload.numero_jugadores,
            id_torneo=id_torneo,
        )
        return {"mensaje": f"Equipo '{equipo['nombre_equipo']}' inscrito exitosamente.", "equipo": equipo}
    except EquipoDuplicadoError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/torneos/{id_torneo}/equipos")
def listar_equipos_endpoint(id_torneo: int):
    try:
        return inscripcion_service.listar_equipos(id_torneo)
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/equipos/{id_equipo}/jugadores")
def inscribir_jugador_endpoint(
    id_equipo: int,
    payload: JugadorCreateRequest,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        jugador = inscripcion_service.inscribir_jugador(
            nombre_jugador=payload.nombre_jugador,
            apellido_paterno=payload.apellido_paterno,
            apellido_materno=payload.apellido_materno,
            dni=payload.dni,
            id_equipo=id_equipo,
        )
        return {"mensaje": f"Jugador '{jugador['nombre_jugador']}' inscrito exitosamente.", "jugador": jugador}
    except JugadorDuplicadoError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/equipos/{id_equipo}/jugadores")
def listar_jugadores_endpoint(id_equipo: int):
    try:
        return inscripcion_service.listar_jugadores(id_equipo)
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))