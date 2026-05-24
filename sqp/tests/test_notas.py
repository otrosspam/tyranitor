"""
tests/test_notas.py
Pruebas unitarias para notas y el servicio académico.
Cobertura actual: ~45% — el equipo debe completar hasta ≥85%.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from src.models.database import reset_db
from src.services.academic_service import (
    es_aprobado, calcular_promedio_estudiante,
    reporte_academico, estadisticas_globales
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpiar_db():
    reset_db()
    yield
    reset_db()


@pytest.fixture
def setup_datos():
    """Crea un estudiante y una materia base para las pruebas."""
    client.post("/estudiantes/", json={
        "codigo": "E001", "nombre": "Ana García",
        "email": "ana@test.com", "semestre": 5
    })
    client.post("/materias/", json={
        "codigo": "CS101", "nombre": "Calidad del Software", "creditos": 3
    })


class TestEsAprobado:

    def test_nota_tres_es_aprobado(self):
        assert es_aprobado(3.0) is True

    def test_nota_mayor_tres_es_aprobado(self):
        assert es_aprobado(4.5) is True

    def test_nota_menor_tres_es_reprobado(self):
        assert es_aprobado(2.9) is False

    def test_nota_cero_es_reprobado(self):
        assert es_aprobado(0.0) is False


class TestRegistrarNota:

    def test_registrar_nota_exitosa(self, setup_datos):
        payload = {
            "codigo_estudiante": "E001",
            "codigo_materia": "CS101",
            "actividad": "Parcial 1",
            "valor": 4.0
        }
        response = client.post("/notas/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["valor"] == pytest.approx(4.0)
        assert data["aprobado"] is True

    def test_registrar_nota_estudiante_inexistente(self, setup_datos):
        payload = {
            "codigo_estudiante": "X999",
            "codigo_materia": "CS101",
            "actividad": "Parcial",
            "valor": 3.0
        }
        response = client.post("/notas/", json=payload)
        assert response.status_code == 404

    def test_registrar_nota_materia_inexistente(self, setup_datos):
        payload = {
            "codigo_estudiante": "E001",
            "codigo_materia": "XX999",
            "actividad": "Parcial",
            "valor": 3.0
        }
        response = client.post("/notas/", json=payload)
        assert response.status_code == 404

    def test_registrar_nota_valor_invalido(self, setup_datos):
        payload = {
            "codigo_estudiante": "E001",
            "codigo_materia": "CS101",
            "actividad": "Parcial",
            "valor": 6.0
        }
        response = client.post("/notas/", json=payload)
        assert response.status_code == 400


class TestReporteAcademico:

    def test_reporte_estudiante_inexistente(self):
        resultado = reporte_academico("X999")
        assert "error" in resultado

    def test_reporte_sin_notas(self):
        # Crear estudiante directamente en DB para prueba de servicio
        from src.models.database import get_estudiantes
        get_estudiantes()["E001"] = {
            "codigo": "E001", "nombre": "Ana", "email": "a@t.com",
            "semestre": 1, "activo": True
        }
        resultado = reporte_academico("E001")
        assert resultado["total_notas"] == 0
        assert resultado["promedio"] == pytest.approx(0.0)


class TestEstadisticasGlobales:

    def test_estadisticas_sin_datos(self):
        stats = estadisticas_globales()
        assert stats["total_estudiantes"] == 0
        assert stats["promedio_global"] == pytest.approx(0.0)


# ─────────────────────────────────────────────────────────────
#  TODO para el equipo:
#  Agregar tests para DOCUMENTAR y CORREGIR las deudas técnicas:
#
#  1. test_division_por_cero_promedio_estudiante:
#     Llama calcular_promedio_estudiante("E001") sin notas.
#     Verifica que lanza ZeroDivisionError (o que fue corregido).
#
#  2. test_notas_de_estudiante_endpoint:
#     GET /notas/estudiante/E001 con notas registradas.
#
#  3. test_promedio_estudiante_endpoint:
#     GET /notas/promedio/estudiante/E001 con ≥1 nota.
#
#  4. test_promedio_materia_endpoint:
#     GET /notas/promedio/materia/CS101 con ≥1 nota.
#
#  5. test_estadisticas_con_datos:
#     Registra varios estudiantes/notas y valida el reporte global.
#
#  6. test_reporte_con_notas_mixtas:
#     Registra notas aprobadas y reprobadas y verifica los conteos.
# ─────────────────────────────────────────────────────────────
