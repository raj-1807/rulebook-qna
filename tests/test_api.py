"""Tests for Rulebook QnA system."""
import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_returns_ok(self):
        """Health endpoint should return 200 with status ok."""
        from backend.main import app
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "rulebook-qna"
