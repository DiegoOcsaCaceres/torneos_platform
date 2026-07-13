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
from typing import Optional
import unicodedata

from app.exceptions import (
    UsuarioDuplicadoError,
    CredencialesInvalidasError,
    RepositorioError,
    TorneoNoEncontradoError,
    TorneoConEquiposError,
    EquipoDuplicadoError,
    JugadorDuplicadoError,
    EquipoConJugadoresError,
    FixtureError,
    ResultadoInvalidoError,
)
from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.torneo_repo import TorneoRepository
from app.services.auth_service import AuthService
from app.services.torneo_service import TorneoService

from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.torneo_repo import TorneoRepository
from app.repositories.equipo_repo import EquipoRepository
from app.repositories.jugador_repo import JugadorRepository
from app.repositories.cancha_repo import CanchaRepository
from app.services.auth_service import AuthService
from app.services.torneo_service import TorneoService
from app.services.inscripcion_service import InscripcionService
from app.services.fixture_service import FixtureService
from app.repositories.partido_repo import PartidoRepository
from app.repositories.resultado_repo import ResultadoRepository
from app.services.resultado_service import ResultadoService

app = FastAPI(title="Canchalibre API", version="1.0.0")

# ── CORS: permite que el frontend le hable a esta API ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://frontend-canchalibre.onrender.com",
    ],
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
cancha_repo = CanchaRepository()
partido_repo = PartidoRepository()
fixture_service = FixtureService(partido_repo, equipo_repo)
resultado_repo = ResultadoRepository()
resultado_service = ResultadoService(resultado_repo, partido_repo, torneo_repo)
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

class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str

class TorneoCreateRequest(BaseModel):
    tipo_deporte: str        # 'futbol' o 'voley'
    nombre_torneo: str
    numero_equipos: int
    fecha_inicio: date
    formato: str = 'liga'    # 'liga' o 'eliminacion_directa'


class EquipoCreateRequest(BaseModel):
    nombre_equipo: str
    numero_jugadores: int

class JugadorCreateRequest(BaseModel):
    nombre_jugador: str
    apellido_paterno: str
    apellido_materno: str
    dni: str


class EquipoUpdateRequest(BaseModel):
    nombre_equipo: str
    id_torneo: int


class JugadorUpdateRequest(BaseModel):
    nombre_jugador: str
    apellido_paterno: str
    apellido_materno: str
    dni: str


class FixtureCreateRequest(BaseModel):
    id_cancha: int
    fecha_inicio: Optional[date] = None
    regenerar: bool = False


class BracketCreateRequest(BaseModel):
    id_cancha: int
    fecha_inicio: Optional[date] = None

class ResultadoCreateRequest(BaseModel):
    id_partido_equipo_local: int
    id_partido_equipo_visita: int
    id_torneo: int
    puntaje_local: int
    puntaje_visita: int
    penales_local: Optional[int] = None
    penales_visita: Optional[int] = None

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

@app.put("/auth/cambiar-password")
def cambiar_password(
    payload: CambiarPasswordRequest,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        auth_service.cambiar_password(
            email=usuario_actual["email"],
            password_actual=payload.password_actual,
            password_nueva=payload.password_nueva,
        )
        return {"mensaje": "Contraseña actualizada exitosamente."}
    except CredencialesInvalidasError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

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
            formato=payload.formato,
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

@app.delete("/torneos/{id_torneo}")
def eliminar_torneo_endpoint(
    id_torneo: int,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        torneo_service.eliminar_torneo(id_torneo)
        return {"mensaje": "Torneo eliminado exitosamente."}
    except TorneoNoEncontradoError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except TorneoConEquiposError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
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

@app.put("/equipos/{id_equipo}")
def actualizar_equipo_endpoint(
    id_equipo: int,
    payload: EquipoUpdateRequest,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        equipo = inscripcion_service.actualizar_equipo(
            id_equipo=id_equipo,
            nombre_equipo=payload.nombre_equipo,
            id_torneo=payload.id_torneo,
        )
        return {"mensaje": f"Equipo actualizado a '{equipo['nombre_equipo']}'.", "equipo": equipo}
    except EquipoDuplicadoError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/equipos/{id_equipo}")
def eliminar_equipo_endpoint(
    id_equipo: int,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        inscripcion_service.eliminar_equipo(id_equipo)
        return {"mensaje": "Equipo eliminado exitosamente."}
    except EquipoConJugadoresError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.put("/jugadores/{id_jugador}")
def actualizar_jugador_endpoint(
    id_jugador: int,
    payload: JugadorUpdateRequest,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        jugador = inscripcion_service.actualizar_jugador(
            id_jugador=id_jugador,
            nombre_jugador=payload.nombre_jugador,
            apellido_paterno=payload.apellido_paterno,
            apellido_materno=payload.apellido_materno,
            dni=payload.dni,
        )
        return {"mensaje": "Jugador actualizado exitosamente.", "jugador": jugador}
    except JugadorDuplicadoError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/jugadores/{id_jugador}")
def eliminar_jugador_endpoint(
    id_jugador: int,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        inscripcion_service.eliminar_jugador(id_jugador)
        return {"mensaje": "Jugador eliminado exitosamente."}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.get("/canchas")
def listar_canchas_endpoint():
    try:
        return cancha_repo.listar()
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/torneos/{id_torneo}/fixture")
def generar_fixture_endpoint(
    id_torneo: int,
    payload: FixtureCreateRequest,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        partidos = fixture_service.generar_fixture(
            id_torneo=id_torneo,
            id_cancha=payload.id_cancha,
            fecha_inicio=payload.fecha_inicio,
            regenerar=payload.regenerar,
        )
        return {"mensaje": f"Fixture generado con {len(partidos)} partido(s).", "partidos": partidos}
    except FixtureError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/torneos/{id_torneo}/fixture")
def ver_fixture_endpoint(id_torneo: int):
    try:
        return fixture_service.ver_fixture(id_torneo)
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/partidos/{id_partido}/resultado")
def registrar_resultado_endpoint(
    id_partido: int,
    payload: ResultadoCreateRequest,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        resultado = resultado_service.registrar_resultado(
            id_partido=id_partido,
            id_partido_equipo_local=payload.id_partido_equipo_local,
            id_partido_equipo_visita=payload.id_partido_equipo_visita,
            id_torneo=payload.id_torneo,
            puntaje_local=payload.puntaje_local,
            puntaje_visita=payload.puntaje_visita,
            penales_local=payload.penales_local,
            penales_visita=payload.penales_visita,
        )
        return {"mensaje": "Resultado registrado exitosamente.", "resultado": resultado}
    except ResultadoInvalidoError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.get("/partidos/{id_partido}/marcador")
def ver_marcador_endpoint(id_partido: int):
    try:
        return resultado_service.ver_marcador(id_partido)
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/torneos/{id_torneo}/bracket")
def generar_bracket_endpoint(
    id_torneo: int,
    payload: BracketCreateRequest,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        partidos = fixture_service.generar_bracket_inicial(
            id_torneo=id_torneo,
            id_cancha=payload.id_cancha,
            fecha_inicio=payload.fecha_inicio,
        )
        return {"mensaje": f"Bracket generado con {len(partidos)} partido(s).", "partidos": partidos}
    except FixtureError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/torneos/{id_torneo}/bracket/siguiente-ronda")
def avanzar_ronda_endpoint(
    id_torneo: int,
    payload: BracketCreateRequest,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    try:
        resultado = fixture_service.generar_siguiente_ronda(
            id_torneo=id_torneo,
            id_cancha=payload.id_cancha,
            fecha_inicio=payload.fecha_inicio,
        )
        if resultado['finalizado']:
            return {
                "mensaje": f"¡Torneo finalizado! Campeón: {resultado['campeon']['nombre_equipo']}.",
                "finalizado": True,
                "campeon": resultado['campeon'],
                "partidos": [],
            }
        return {
            "mensaje": f"Siguiente ronda generada con {len(resultado['partidos'])} partido(s).",
            "finalizado": False,
            "campeon": None,
            "partidos": resultado['partidos'],
        }
    except FixtureError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except RepositorioError as exc:
        raise HTTPException(status_code=500, detail=str(exc))