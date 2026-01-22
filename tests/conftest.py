"""
AutoE2E Test Configuration for Resume Analyzer
"""
import pytest
import requests
import os

# Use localhost for Windows, or host.docker.internal for Docker/WSL
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:6000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")


@pytest.fixture(scope="session")
def ai_service_url():
    return AI_SERVICE_URL


@pytest.fixture(scope="session")
def backend_url():
    return BACKEND_URL


@pytest.fixture(scope="session")
def sample_resume():
    """Create a minimal PDF for testing."""
    pdf_content = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length 200 >> stream
BT /F1 12 Tf 72 750 Td (John Doe - Software Engineer) Tj 0 -20 Td (Skills: Python, Java, React, AWS, Docker) Tj ET
endstream endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref 0 6
trailer << /Size 6 /Root 1 0 R >>
startxref 595
%%EOF"""
    return pdf_content


@pytest.fixture(scope="session")
def sample_job_description():
    return """
    Senior Software Engineer
    
    Requirements:
    - 5+ years of experience in software development
    - Strong proficiency in Python, Java, or JavaScript
    - Experience with React or Angular
    - Knowledge of AWS or Azure
    - Experience with Docker and Kubernetes
    """
