"""
src/routers/estudiantes.py
Endpoints para gestión de estudiantes.

DEUDA TÉCNICA:
  - [MEDIA] Sin validación de formato de email con EmailStr
  - [MEDIA] Código de respuesta HTTP hardcodeado como magic number
  - [BAJA]  Sin paginación en el endpoint de listado
"""
from fastapi import APIRouter, HTTPException
from src.models.schemas import EstudianteCreate, EstudianteResponse
from src.models.database import get_estudiantes
MENSAJE_ESTUDIANTE_NO_ENCONTRADO = "Estudiante no encontrado"

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])


@router.post("/", response_model=EstudianteResponse, status_code=201)
def crear_estudiante(estudiante: EstudianteCreate):
    db = get_estudiantes()
    codigo = estudiante.codigo.strip().upper()

    if codigo in db:
        raise HTTPException(status_code=400, detail="El código ya existe")

    if "@" not in estudiante.email:
        raise HTTPException(status_code=400, detail="Email inválido")

    if not (1 <= estudiante.semestre <= 10):
        raise HTTPException(status_code=400, detail="Semestre debe estar entre 1 y 10")

    db[codigo] = {
        "codigo": codigo,
        "nombre": estudiante.nombre.strip(),
        "email": estudiante.email.strip().lower(),
        "semestre": estudiante.semestre,
        "activo": True,
    }
    return db[codigo]


@router.get("/", response_model=list[EstudianteResponse])
def listar_estudiantes():
    # [DEUDA] Sin paginación — podría retornar miles de registros
    return list(get_estudiantes().values())


@router.get("/{codigo}", response_model=EstudianteResponse)
def obtener_estudiante(codigo: str):
    db = get_estudiantes()
    codigo = codigo.upper()
    if codigo not in db:
        raise HTTPException(status_code=404, detail=MENSAJE_ESTUDIANTE_NO_ENCONTRADO)
    return db[codigo]


@router.delete("/{codigo}", status_code=204)
def eliminar_estudiante(codigo: str):
    db = get_estudiantes()
    codigo = codigo.upper()
    if codigo not in db:
        raise HTTPException(status_code=404, detail=MENSAJE_ESTUDIANTE_NO_ENCONTRADO)
    del db[codigo]


@router.put("/{codigo}/desactivar", response_model=EstudianteResponse)
def desactivar_estudiante(codigo: str):
    db = get_estudiantes()
    codigo = codigo.upper()
    if codigo not in db:
        raise HTTPException(status_code=404, detail=MENSAJE_ESTUDIANTE_NO_ENCONTRADO)
    db[codigo]["activo"] = False
    return db[codigo]
