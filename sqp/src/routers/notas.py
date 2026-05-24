"""
src/routers/notas.py
Endpoints para gestión de notas y reportes.

DEUDA TÉCNICA:
  - [ALTA]  Llamadas al servicio sin manejo de ZeroDivisionError
  - [MEDIA] Lógica de negocio dentro del router (sin capa de servicio)
"""
from fastapi import APIRouter, HTTPException
from src.models.schemas import NotaCreate, NotaResponse
from src.models.database import get_notas, get_estudiantes, get_materias, next_nota_id
from src.services.academic_service import (
    calcular_promedio_estudiante, calcular_promedio_materia,
    reporte_academico, estadisticas_globales, es_aprobado
)
MENSAJE_ESTUDIANTE_NO_ENCONTRADO = "Estudiante no encontrado"
MENSAJE_MATERIA_NO_ENCONTRADA = "Materia no encontrada"

router = APIRouter(prefix="/notas", tags=["Notas"])


@router.post("/", response_model=NotaResponse, status_code=201)
def registrar_nota(nota: NotaCreate):
    codigo_e = nota.codigo_estudiante.strip().upper()
    codigo_m = nota.codigo_materia.strip().upper()

    if codigo_e not in get_estudiantes():
        raise HTTPException(status_code=404, detail=MENSAJE_ESTUDIANTE_NO_ENCONTRADO)

    if codigo_m not in get_materias():
        raise HTTPException(status_code=404, detail=MENSAJE_MATERIA_NO_ENCONTRADA)

    # [DEUDA MEDIA] Magic numbers 0.0 y 5.0 como límites
    if not (0.0 <= nota.valor <= 5.0):
        raise HTTPException(status_code=400,
                            detail="La nota debe estar entre 0.0 y 5.0")

    nueva = {
        "id": next_nota_id(),
        "codigo_estudiante": codigo_e,
        "codigo_materia": codigo_m,
        "actividad": nota.actividad.strip(),
        "valor": round(nota.valor, 2),
        "aprobado": es_aprobado(nota.valor),
    }
    get_notas().append(nueva)
    return nueva


@router.get("/estudiante/{codigo}")
def notas_de_estudiante(codigo: str):
    codigo = codigo.upper()
    if codigo not in get_estudiantes():
        raise HTTPException(status_code=404, detail=MENSAJE_ESTUDIANTE_NO_ENCONTRADO)
    notas = [n for n in get_notas() if n["codigo_estudiante"] == codigo]
    return notas


@router.get("/materia/{codigo}")
def notas_de_materia(codigo: str):
    codigo = codigo.upper()
    if codigo not in get_materias():
        raise HTTPException(status_code=404, detail=MENSAJE_MATERIA_NO_ENCONTRADA)
    notas = [n for n in get_notas() if n["codigo_materia"] == codigo]
    return notas


@router.get("/promedio/estudiante/{codigo}")
def promedio_estudiante(codigo: str):
    codigo = codigo.upper()
    if codigo not in get_estudiantes():
        raise HTTPException(status_code=404, detail=MENSAJE_ESTUDIANTE_NO_ENCONTRADO)
    # [DEUDA ALTA] Sin manejo de ZeroDivisionError si no hay notas
    promedio = calcular_promedio_estudiante(codigo)
    return {"codigo": codigo, "promedio": promedio}


@router.get("/promedio/materia/{codigo}")
def promedio_materia(codigo: str):
    codigo = codigo.upper()
    if codigo not in get_materias():
        raise HTTPException(status_code=404, detail=MENSAJE_MATERIA_NO_ENCONTRADA)
    # [DEUDA ALTA] Sin manejo de ZeroDivisionError si no hay notas
    promedio = calcular_promedio_materia(codigo)
    return {"codigo": codigo, "promedio": promedio}


@router.get("/reporte/{codigo_estudiante}")
def reporte_estudiante(codigo_estudiante: str):
    return reporte_academico(codigo_estudiante.upper())


@router.get("/estadisticas/globales")
def estadisticas():
    return estadisticas_globales()
