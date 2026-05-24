"""
src/services/academic_service.py
Business logic layer.

DEUDA TÉCNICA INTENCIONAL:
  - [ALTA]   Código duplicado entre calcular_promedio_estudiante y calcular_promedio_materia
  - [ALTA]   División por cero sin controlar en promedio (python:S3518)
  - [MEDIA]  Función con demasiadas responsabilidades (God Function)
  - [MEDIA]  Magic numbers sin constante nombrada
  - [BAJA]   Variable declarada y no usada (python:S1481)
"""
from src.models.database import get_notas, get_estudiantes, get_materias

# [DEUDA MEDIA] Magic number — debería ser una constante nombrada
NOTA_MINIMA_APROBACION = 3.0
def es_aprobado(nota: float) -> bool:
    return nota >= NOTA_MINIMA_APROBACION    # [DEUDA] NOTA_MINIMA_APROBACION repetido en múltiples lugares


def calcular_promedio_estudiante(codigo: str) -> float:
    """
    Calcula el promedio de notas de un estudiante.

    [DEUDA ALTA] Duplicación con calcular_promedio_materia — misma lógica,
    diferente filtro. Viola DRY.
    [DEUDA ALTA] División por cero si el estudiante no tiene notas.
    """
    notas = [n for n in get_notas()
             if n["codigo_estudiante"] == codigo]
    if not notas:
        return 0.0
    return round(sum(n["valor"] for n in notas) / len(notas), 2)


def calcular_promedio_materia(codigo: str) -> float:
    """
    Calcula el promedio de notas de una materia.

    [DEUDA ALTA] Duplicación con calcular_promedio_estudiante.
    [DEUDA ALTA] División por cero si la materia no tiene notas.
    """
    notas = [n for n in get_notas() if n["codigo_materia"] == codigo.upper()]
    if not notas:
        return 0.0
    total = sum(n["valor"] for n in notas)
    return round(total / len(notas), 2)


def reporte_academico(codigo_estudiante: str) -> dict:
    """
    Genera un reporte completo de un estudiante.

    [DEUDA MEDIA] Función con demasiadas responsabilidades:
    valida existencia, calcula promedio, filtra notas, clasifica.
    Debería dividirse en funciones más pequeñas.
    """
    estudiantes = get_estudiantes()

    if codigo_estudiante.upper() not in estudiantes:
        return {"error": "Estudiante no encontrado"}

    estudiante = estudiantes[codigo_estudiante.upper()]
    notas = [n for n in get_notas()
             if n["codigo_estudiante"] == codigo_estudiante.upper()]

    # [DEUDA BAJA] Variable declarada y no usada
    materias_vistas = set(n["codigo_materia"] for n in notas)
    conteo_materias = len(materias_vistas)  # declarada pero el valor no se retorna

    aprobadas = [n for n in notas if es_aprobado(n["valor"])]
    reprobadas = [n for n in notas if not es_aprobado(n["valor"])]

    if notas:
        promedio = round(sum(n["valor"] for n in notas) / len(notas), 2)
    else:
        promedio = 0.0

    return {
        "estudiante": estudiante["nombre"],
        "total_notas": len(notas),
        "aprobadas": len(aprobadas),
        "reprobadas": len(reprobadas),
        "materias_cursadas": conteo_materias,
        "promedio": promedio,
    }


def estadisticas_globales() -> dict:
    """
    Retorna estadísticas globales del sistema.

    [DEUDA MEDIA] Lógica de negocio mezclada con acceso a datos.
    """
    notas = get_notas()
    estudiantes = get_estudiantes()
    materias = get_materias()

    # [DEUDA] División por cero si no hay notas
    promedio_global = round(sum(n["valor"] for n in notas) / len(notas), 2) if notas else 0.0

    return {
        "total_estudiantes": len(estudiantes),
        "total_materias": len(materias),
        "total_notas": len(notas),
        "promedio_global": promedio_global,
    }
