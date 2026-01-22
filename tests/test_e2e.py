"""
E2E Tests - Full workflow tests for Resume Analyzer
Run: pytest tests/test_e2e.py -v
"""
import pytest
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestAnalyzeWorkflow:
    """End-to-end tests for the resume analysis workflow."""

    def test_analyze_resume_success(self, ai_service_url, sample_resume, sample_job_description):
        """Full analysis should complete successfully."""
        files = {"file": ("resume.pdf", sample_resume, "application/pdf")}
        data = {"jobDescriptionText": sample_job_description}
        
        response = requests.post(
            f"{ai_service_url}/api/analyze",
            files=files,
            data=data,
            timeout=120
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify response structure
        assert "matchScore" in result or "accuracy" in result
        assert "skills" in result or "matchedSkills" in result

    def test_analyze_returns_recommendations(self, ai_service_url, sample_resume, sample_job_description):
        """Analysis should return ATS recommendations."""
        files = {"file": ("resume.pdf", sample_resume, "application/pdf")}
        data = {"jobDescriptionText": sample_job_description}
        
        response = requests.post(
            f"{ai_service_url}/api/analyze",
            files=files,
            data=data,
            timeout=120
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should have recommendations
        assert "atsRecommendations" in result or "careerAdvice" in result


class TestConcurrency:
    """Concurrency and load tests."""

    def test_concurrent_requests_10_users(self, ai_service_url, sample_resume, sample_job_description):
        """Service should handle 10 concurrent users."""
        num_concurrent = 10
        results = []
        
        def make_request():
            try:
                files = {"file": ("resume.pdf", sample_resume, "application/pdf")}
                data = {"jobDescriptionText": sample_job_description}
                start = time.time()
                response = requests.post(
                    f"{ai_service_url}/api/analyze",
                    files=files,
                    data=data,
                    timeout=120
                )
                elapsed = time.time() - start
                return {"success": response.status_code == 200, "time": elapsed}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(make_request) for _ in range(num_concurrent)]
            for future in as_completed(futures):
                results.append(future.result())
        
        success_count = sum(1 for r in results if r.get("success"))
        success_rate = (success_count / num_concurrent) * 100
        
        assert success_rate >= 80, f"Success rate {success_rate}% is below 80%"

    def test_concurrent_requests_50_users(self, ai_service_url, sample_resume, sample_job_description):
        """Service should handle 50 concurrent users with high success rate."""
        num_concurrent = 50
        results = []
        
        def make_request():
            try:
                files = {"file": ("resume.pdf", sample_resume, "application/pdf")}
                data = {"jobDescriptionText": sample_job_description}
                start = time.time()
                response = requests.post(
                    f"{ai_service_url}/api/analyze",
                    files=files,
                    data=data,
                    timeout=180
                )
                elapsed = time.time() - start
                return {"success": response.status_code == 200, "time": elapsed}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(make_request) for _ in range(num_concurrent)]
            for future in as_completed(futures):
                results.append(future.result())
        
        success_count = sum(1 for r in results if r.get("success"))
        success_rate = (success_count / num_concurrent) * 100
        
        # 50 concurrent should have at least 90% success
        assert success_rate >= 90, f"Success rate {success_rate}% is below 90%"


class TestResilience:
    """Resilience and error handling tests."""

    def test_invalid_file_returns_error(self, ai_service_url, sample_job_description):
        """Invalid file should return appropriate error."""
        files = {"file": ("invalid.txt", b"not a pdf", "text/plain")}
        data = {"jobDescriptionText": sample_job_description}
        
        response = requests.post(
            f"{ai_service_url}/api/analyze",
            files=files,
            data=data,
            timeout=30
        )
        
        # Should return 400 for invalid input
        assert response.status_code in [400, 422, 500]

    def test_missing_job_description_returns_error(self, ai_service_url, sample_resume):
        """Missing job description should return error."""
        files = {"file": ("resume.pdf", sample_resume, "application/pdf")}
        
        response = requests.post(
            f"{ai_service_url}/api/analyze",
            files=files,
            timeout=30
        )
        
        assert response.status_code in [400, 422]
