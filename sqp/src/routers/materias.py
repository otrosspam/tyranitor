"""
src/routers/materias.py
Endpoints para gestión de materias.
"""
from fastapi import APIRouter, HTTPException
from src.models.schemas import MateriaCreate, MateriaResponse
from src.models.database import get_materias

router = APIRouter(prefix="/materias", tags=["Materias"])
MENSAJE_ESTUDIANTE_NO_ENCONTRADO = "Estudiante no encontrado"
MENSAJE_MATERIA_NO_ENCONTRADA = "Materia no encontrada"

@router.post("/", response_model=MateriaResponse, status_code=201)
def crear_materia(materia: MateriaCreate):
    db = get_materias()
    codigo = materia.codigo.strip().upper()

    if codigo in db:
        raise HTTPException(status_code=400, detail="El código ya existe")

    # [DEUDA MEDIA] Magic numbers: 1 y 6 deberían ser constantes
    if not (1 <= materia.creditos <= 6):
        raise HTTPException(status_code=400,
                            detail="Créditos deben estar entre 1 y 6")

    db[codigo] = {
        "codigo": codigo,
        "nombre": materia.nombre.strip(),
        "creditos": materia.creditos,
        "descripcion": str(materia.descripcion) if materia.descripcion else None,
    }
    return db[codigo]


@router.get("/", response_model=list[MateriaResponse])
def listar_materias():
    return list(get_materias().values())


@router.get("/{codigo}", response_model=MateriaResponse)
def obtener_materia(codigo: str):
    db = get_materias()
    codigo = codigo.upper()
    if codigo not in db:
        raise HTTPException(status_code=404, detail=MENSAJE_MATERIA_NO_ENCONTRADA)
    return db[codigo]


@router.delete("/{codigo}", status_code=204)
def eliminar_materia(codigo: str):
    db = get_materias()
    codigo = codigo.upper()
    if codigo not in db:
        raise HTTPException(status_code=404, detail=MENSAJE_MATERIA_NO_ENCONTRADA)
    del db[codigo]
