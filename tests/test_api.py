"""
Tests para la API de Música.
Pruebas unitarias y de integración usando pytest.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app
from app.database import get_session
from app.models import Usuario, Cancion, Favorito

OK_CREADO = (200, 201)
OK_BORRADO = (200, 204)
ERROR_DUPLICADO = (400, 409)
# =============================================================================
# CONFIGURACIÓN DE FIXTURES
# =============================================================================

# Fixture para crear una base de datos en memoria para testing
@pytest.fixture(name="session")
def session_fixture():
    """
    Crea una sesión de base de datos en memoria para cada test.
    Se limpia automáticamente después de cada test.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


# Fixture para cliente de pruebas
@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Crea un cliente de pruebas de FastAPI con la sesión de test.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# TODO: Fixture para crear usuarios de prueba
@pytest.fixture(name="usuario_test")
def usuario_test_fixture(session: Session):
    """
    Crea un usuario de prueba en la base de datos.
    """
    usuario = Usuario(nombre="Usuario Test", correo="test@example.com")
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


# TODO: Fixture para crear canciones de prueba
@pytest.fixture(name="musica_test")
def cancion_test_fixture(session: Session):
    """
    Crea una cancion de prueba en la base de datos.
    """
    cancion = Cancion(
        titulo="canción Test",
        director="Director Test",
        genero="Drama",
        duracion=120,
        año=2020,
        clasificacion="PG-13",
        sinopsis="Una canción de prueba"
    )
    session.add(cancion)
    session.commit()
    session.refresh(cancion)
    return cancion



# =============================================================================
# TESTS DE USUARIOS
# =============================================================================

class TestUsuarios:
    """Tests para los endpoints de usuarios."""
    
    # TODO: Test para listar usuarios
    def test_listar_usuarios(self, client: TestClient):
        """Test para GET /api/usuarios"""
        response = client.get("/api/usuarios")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["correo"] == "test@example.com"
    
    # TODO: Test para crear usuario
    def test_crear_usuario(self, client: TestClient):
        """Test para POST /api/usuarios"""
        response = client.post(
            "/api/usuarios",
            json={"nombre": "Ana", "correo": "ana@example.com"},
        )
        assert response.status_code in OK_CREADO
        data = response.json()
        assert data["nombre"] == "Ana"
        assert data["correo"] == "ana@example.com"
        assert "id" in data
    
    # TODO: Test para crear usuario con correo duplicado
    def test_crear_usuario_correo_duplicado(self, client: TestClient, usuario_test: Usuario):
        """Test para verificar que no se permiten correos duplicados"""
        response = client.post(
            "/api/usuarios",
            json={"nombre": "Otro", "correo": usuario_test.correo},
        )
        assert response.status_code in ERROR_DUPLICADO
    
    # TODO: Test para obtener usuario por ID
    def test_obtener_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para GET /api/usuarios/{id}"""
        response = client.get(f"/api/usuarios/{usuario_test.id}")
        assert response.status_code == 200
        assert response.json()["nombre"] == "Usuario Test"
    
    # TODO: Test para obtener usuario inexistente
    def test_obtener_usuario_no_existe(self, client: TestClient):
        """Test para verificar error 404 con usuario inexistente"""
        response = client.get("/api/usuarios/9999")
        assert response.status_code == 404
    
    # TODO: Test para actualizar usuario
    def test_actualizar_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para PUT /api/usuarios/{id}"""
        response = client.put(
            f"/api/usuarios/{usuario_test.id}",
            json={"nombre": "Nombre Nuevo", "correo": "nuevo@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Nombre Nuevo"
        assert data["correo"] == "nuevo@example.com"
    
    # TODO: Test para eliminar usuario
    def test_eliminar_usuario(self, client: TestClient, usuario_test: Usuario):
        """Test para DELETE /api/usuarios/{id}"""
        response = client.delete(f"/api/usuarios/{usuario_test.id}")
        assert response.status_code in OK_BORRADO
        assert client.get(f"/api/usuarios/{usuario_test.id}").status_code == 404


# =============================================================================
# TESTS DE canciónS
# =============================================================================

class TestCancions:
    """Tests para los endpoints de cancións."""
    
    # TODO: Test para listar cancións
    def test_listar_cancions(self, client: TestClient):
        """Test para GET /api/cancions"""
        response = client.get("/api/canciones")
        assert response.status_code == 200
        assert len(response.json()) == 1
    
    # TODO: Test para crear canción
    def test_crear_cancion(self, client: TestClient):
        """Test para POST /api/cancions"""
        response = client.post("/api/canciones", json=datos_cancion())
        assert response.status_code in OK_CREADO
        data = response.json()
        assert data["titulo"] == "Nueva Canción"
        assert data["año"] == 2021
        assert "id" in data
    
    # TODO: Test para obtener canción por ID
    def test_obtener_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para GET /api/cancions/{id}"""
        response = client.get(f"/api/canciones/{cancion_test.id}")
        assert response.status_code == 200
        assert response.json()["titulo"] == "Canción Test"
    
    # TODO: Test para actualizar canción
    def test_actualizar_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para PUT /api/cancions/{id}"""
        response = client.put(
            f"/api/canciones/{cancion_test.id}",
            json=datos_cancion(titulo="Título Actualizado"),
        )
        assert response.status_code == 200
        assert response.json()["titulo"] == "Título Actualizado"
    
    # TODO: Test para eliminar canción
    def test_eliminar_cancion(self, client: TestClient, cancion_test: Cancion):
        """Test para DELETE /api/cancions/{id}"""
        response = client.delete(f"/api/canciones/{cancion_test.id}")
        assert response.status_code in OK_BORRADO
        assert client.get(f"/api/canciones/{cancion_test.id}").status_code == 404
    
    # TODO: Test para buscar cancións
    def test_buscar_cancions(self, client: TestClient, cancion_test: Cancion):
        """Test para GET /api/cancions/buscar"""
        response = client.get("/api/canciones/buscar", params={"genero": "Rock"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["titulo"] == "Canción Test"
    
    # TODO: Test para buscar cancións con múltiples filtros
    def test_buscar_cancions_multiples_filtros(self, client: TestClient):
        """Test para búsqueda con múltiples parámetros"""
        client.post(
            "/api/canciones",
            json=datos_cancion(artista="Artista Test", genero="Pop"),
        )
        response = client.get(
            "/api/canciones/buscar",
            params={"artista": "Artista Test", "genero": "Rock"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["genero"] == "Rock"


# =============================================================================
# TESTS DE FAVORITOS
# =============================================================================

class TestFavoritos:
    """Tests para los endpoints de favoritos."""
    
    # TODO: Test para listar favoritos
    def test_listar_favoritos(self, client: TestClient):
        """Test para GET /api/favoritos"""
        response = client.get("/api/favoritos")
        assert response.status_code == 200
        assert response.json() == []
    
    # TODO: Test para crear favorito
    def test_crear_favorito(
        self, 
        client: TestClient, 
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para POST /api/favoritos"""
        response = client.post(
            "/api/favoritos",
            json={"id_usuario": usuario_test.id, "id_cancion": cancion_test.id},
        )
        assert response.status_code in OK_CREADO
        data = response.json()
        assert data["id_usuario"] == usuario_test.id
        assert data["id_cancion"] == cancion_test.id
    
    # TODO: Test para crear favorito duplicado
    def test_crear_favorito_duplicado(
        self, 
        client: TestClient, 
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para verificar que no se permiten favoritos duplicados"""
        payload = {"id_usuario": usuario_test.id, "id_cancion": cancion_test.id}
        client.post("/api/favoritos", json=payload)
        response = client.post("/api/favoritos", json=payload)
        assert response.status_code in ERROR_DUPLICADO
    
    # TODO: Test para eliminar favorito
    def test_eliminar_favorito(
        self, 
        client: TestClient, 
        session: Session,
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para DELETE /api/favoritos/{id}"""

        pass
    
    # TODO: Test para marcar favorito desde usuario
    def test_marcar_favorito_usuario(
        self, 
        client: TestClient, 
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para POST /api/usuarios/{id}/favoritos/{id_cancion}"""

        pass
    
    # TODO: Test para listar favoritos de usuario
    def test_listar_favoritos_usuario(
        self, 
        client: TestClient, 
        session: Session,
        usuario_test: Usuario, 
        cancion_test: Cancion
    ):
        """Test para GET /api/usuarios/{id}/favoritos"""

        pass


# =============================================================================
# TESTS DE INTEGRACIÓN
# =============================================================================

class TestIntegracion:
    """Tests de integración que prueban flujos completos."""
    
    # TODO: Test de flujo completo: crear usuario, canción y marcar favorito
    def test_flujo_completo(self, client: TestClient):
        """Test que verifica el flujo completo de la aplicación"""
        # 1. Crear usuario

        # 2. Crear canción

        # 3. Marcar como favorito

        # 4. Verificar que aparece en favoritos del usuario

        pass


# =============================================================================
# TESTS DE VALIDACIÓN
# =============================================================================

class TestValidacion:
    """Tests para validaciones de datos."""
    
    # TODO: Test para validar email inválido
    def test_email_invalido(self, client: TestClient):
        """Test para verificar validación de email"""

        pass
    
    # TODO: Test para validar año de canción
    def test_año_cancion_invalido(self, client: TestClient):
        """Test para verificar validación de año"""

        pass
    
    # TODO: Test para validar campos requeridos
    def test_campos_requeridos(self, client: TestClient):
        """Test para verificar que los campos requeridos son obligatorios"""

        pass


