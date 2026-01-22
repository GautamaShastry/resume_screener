"""
Smoke Tests - Basic health and availability checks
Run: pytest tests/test_smoke.py -v
"""
import pytest
import requests


class TestSmoke:
    """Smoke tests to verify services are running."""

    def test_ai_service_health(self, ai_service_url):
        """AI service should return healthy status."""
        response = requests.get(f"{ai_service_url}/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_ai_service_analyze_endpoint_exists(self, ai_service_url):
        """Analyze endpoint should exist (even if it returns 400 without data)."""
        response = requests.post(f"{ai_service_url}/api/analyze", timeout=10)
        # 400 is acceptable - means endpoint exists but needs proper data
        assert response.status_code in [200, 400]

    def test_backend_actuator_available(self, backend_url):
        """Backend actuator endpoints should be available."""
        # This may return 401 if secured, which is fine
        response = requests.get(f"{backend_url}/actuator/health", timeout=10)
        assert response.status_code in [200, 401, 403]
