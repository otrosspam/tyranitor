"""
tests/test_estudiantes.py
Pruebas unitarias para el módulo de estudiantes.
Cobertura actual: ~55% — el equipo debe completar hasta ≥85%.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from src.models.database import reset_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpiar_db():
    """Limpia la base de datos antes de cada test."""
    reset_db()
    yield
    reset_db()


class TestCrearEstudiante:

    def test_crear_estudiante_exitoso(self):
        payload = {
            "codigo": "E001",
            "nombre": "Ana García",
            "email": "ana@test.com",
            "semestre": 5
        }
        response = client.post("/estudiantes/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["codigo"] == "E001"
        assert data["nombre"] == "Ana García"
        assert data["activo"] is True

    def test_crear_estudiante_codigo_duplicado(self):
        payload = {"codigo": "E001", "nombre": "Ana", "email": "a@t.com", "semestre": 1}
        client.post("/estudiantes/", json=payload)
        response = client.post("/estudiantes/", json=payload)
        assert response.status_code == 400

    def test_crear_estudiante_email_invalido(self):
        payload = {"codigo": "E002", "nombre": "Pedro", "email": "sinatsign", "semestre": 2}
        response = client.post("/estudiantes/", json=payload)
        assert response.status_code == 400

    def test_crear_estudiante_semestre_invalido(self):
        payload = {"codigo": "E003", "nombre": "Luis", "email": "l@t.com", "semestre": 11}
        response = client.post("/estudiantes/", json=payload)
        assert response.status_code == 400


class TestObtenerEstudiante:

    def test_obtener_estudiante_existente(self):
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana", "email": "a@t.com", "semestre": 3
        })
        response = client.get("/estudiantes/E001")
        assert response.status_code == 200
        assert response.json()["codigo"] == "E001"

    def test_obtener_estudiante_inexistente(self):
        response = client.get("/estudiantes/X999")
        assert response.status_code == 404


class TestListarEstudiantes:

    def test_listar_vacio(self):
        response = client.get("/estudiantes/")
        assert response.status_code == 200
        assert response.json() == []

    def test_listar_con_estudiantes(self):
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana", "email": "a@t.com", "semestre": 1
        })
        response = client.get("/estudiantes/")
        assert len(response.json()) == 1


class TestEliminarEstudiante:

    def test_eliminar_estudiante_existente(self):
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana", "email": "a@t.com", "semestre": 1
        })
        response = client.delete("/estudiantes/E001")
        assert response.status_code == 204
        assert client.get("/estudiantes/E001").status_code == 404

    def test_eliminar_estudiante_inexistente(self):
        response = client.delete("/estudiantes/X999")
        assert response.status_code == 404


class TestActualizarEstudiante:

    def test_desactivar_estudiante(self):
        client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana", "email": "a@t.com", "semestre": 1
        })
        response = client.put("/estudiantes/E001/desactivar")
        assert response.status_code == 200
        assert response.json()["activo"] is False


class TestValidacionesEstudiante:

    def test_codigo_se_convierte_a_mayusculas(self):
        response = client.post("/estudiantes/", json={
            "codigo": "e001", "nombre": "Ana", "email": "a@t.com", "semestre": 1
        })
        assert response.status_code == 201
        assert response.json()["codigo"] == "E001"

    def test_semestre_minimo_valido(self):
        response = client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana", "email": "a@t.com", "semestre": 1
        })
        assert response.status_code == 201
        assert response.json()["semestre"] == 1

    def test_semestre_maximo_valido(self):
        response = client.post("/estudiantes/", json={
            "codigo": "E001", "nombre": "Ana", "email": "a@t.com", "semestre": 10
        })
        assert response.status_code == 201
        assert response.json()["semestre"] == 10
