"""Tests for the main FastAPI application."""
from app.app import app


class TestApp:
    """Test cases for the main FastAPI application."""

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to Inventory Management API"}

    def test_health_check_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_app_metadata(self):
        """Test FastAPI app metadata."""
        assert app.title == "Inventory Management API"
        assert app.description == "A comprehensive inventory management system with AI chatbot integration"
        assert app.version == "1.0.0"

    def test_api_docs_accessible(self, client):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema_accessible(self, client):
        """Test that OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "Inventory Management API"
        assert schema["info"]["version"] == "1.0.0"

    def test_invalid_endpoint(self, client):
        """Test accessing an invalid endpoint."""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404