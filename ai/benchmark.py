"""
Benchmark script to measure and prove metrics for your resume.
Run this after starting the AI service (python app.py)

Usage:
    python benchmark.py --test latency
    python benchmark.py --test accuracy
    python benchmark.py --test concurrency
    python benchmark.py --test all
"""

import requests
import time
import statistics
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

API_URL = "http://localhost:6000"

# Thread-safe counter
request_counter = threading.Lock()
total_processed = 0

# Check if reportlab is available for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# Sample test data
SAMPLE_JOB_DESCRIPTION = """
Senior Software Engineer

Requirements:
- 5+ years of experience in software development
- Strong proficiency in Python, Java, or JavaScript
- Experience with React or Angular frontend frameworks
- Knowledge of AWS or Azure cloud platforms
- Experience with Docker and Kubernetes
- Strong understanding of REST APIs and microservices
- Experience with PostgreSQL or MySQL databases
- Excellent problem-solving skills
- Bachelor's degree in Computer Science or related field

Nice to have:
- Experience with machine learning
- Knowledge of CI/CD pipelines
- Experience with Agile methodologies
"""

def create_sample_resume():
    """Create a sample resume PDF file for testing"""
    resume_text = """John Doe
Software Engineer

Skills: Python, JavaScript, React, Node.js, AWS, Docker, PostgreSQL, REST APIs

Experience:
- Senior Developer at Tech Corp (3 years)
- Built scalable web applications using React and Node.js
- Deployed applications on AWS using Docker containers

Education:
- BS Computer Science, State University
"""
    
    if HAS_REPORTLAB:
        # Create a proper PDF
        pdf_path = "test_resume.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        # Write text to PDF
        y = 750
        for line in resume_text.strip().split('\n'):
            c.drawString(72, y, line)
            y -= 15
        
        c.save()
        return pdf_path
    else:
        # Fallback: create a minimal PDF manually (basic PDF structure)
        pdf_path = "test_resume.pdf"
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 200 >>
stream
BT
/F1 12 Tf
72 750 Td
(John Doe - Software Engineer) Tj
0 -20 Td
(Skills: Python, JavaScript, React, Node.js, AWS, Docker, PostgreSQL) Tj
0 -20 Td
(Experience: 3 years at Tech Corp) Tj
0 -20 Td
(Education: BS Computer Science) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000518 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
595
%%EOF"""
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        return pdf_path


def test_latency(num_requests=20):
    """
    Measure response time latency.
    Returns p50, p95, p99 metrics.
    """
    print(f"\n{'='*60}")
    print("LATENCY TEST")
    print(f"{'='*60}")
    print(f"Running {num_requests} requests...")
    
    resume_file = create_sample_resume()
    times = []
    errors = 0
    
    for i in range(num_requests):
        try:
            with open(resume_file, 'rb') as f:
                start = time.time()
                response = requests.post(
                    f"{API_URL}/api/analyze",
                    files={"file": ("resume.pdf", f, "application/pdf")},
                    data={"jobDescriptionText": SAMPLE_JOB_DESCRIPTION},
                    timeout=120
                )
                elapsed = time.time() - start
                
                if response.status_code == 200:
                    times.append(elapsed)
                    print(f"  Request {i+1}: {elapsed:.2f}s ✓")
                else:
                    errors += 1
                    print(f"  Request {i+1}: Error {response.status_code} - {response.text[:100]}")
        except Exception as e:
            errors += 1
            print(f"  Request {i+1}: Exception - {str(e)[:50]}")
    
    if times:
        times_sorted = sorted(times)
        results = {
            "total_requests": num_requests,
            "successful": len(times),
            "errors": errors,
            "min": min(times),
            "max": max(times),
            "avg": statistics.mean(times),
            "p50": times_sorted[int(len(times) * 0.50)],
            "p95": times_sorted[int(len(times) * 0.95)] if len(times) >= 20 else times_sorted[-1],
            "p99": times_sorted[int(len(times) * 0.99)] if len(times) >= 100 else times_sorted[-1],
        }
        
        print(f"\n{'='*60}")
        print("LATENCY RESULTS")
        print(f"{'='*60}")
        print(f"  Total Requests:  {results['total_requests']}")
        print(f"  Successful:      {results['successful']}")
        print(f"  Errors:          {results['errors']}")
        print(f"  Error Rate:      {(errors/num_requests)*100:.1f}%")
        print(f"  ")
        print(f"  Min:             {results['min']:.2f}s")
        print(f"  Max:             {results['max']:.2f}s")
        print(f"  Average:         {results['avg']:.2f}s")
        print(f"  p50 (median):    {results['p50']:.2f}s")
        print(f"  p95:             {results['p95']:.2f}s")
        print(f"  p99:             {results['p99']:.2f}s")
        print(f"{'='*60}")
        
        # Resume bullet point suggestion
        print("\n📝 RESUME BULLET POINT:")
        print(f"  'Achieved p95 latency of {results['p95']:.1f}s for AI-powered resume analysis'")
        
        return results
    else:
        print("No successful requests!")
        return None


def create_test_pdf(content, filename="temp_resume.pdf"):
    """Create a PDF with given content for testing"""
    if HAS_REPORTLAB:
        c = canvas.Canvas(filename, pagesize=letter)
        y = 750
        for line in content.strip().split('\n'):
            c.drawString(72, y, line[:80])  # Truncate long lines
            y -= 15
        c.save()
    else:
        # Minimal PDF with content
        pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 300 >>
stream
BT
/F1 10 Tf
72 750 Td
({content[:200].replace(chr(10), ') Tj 0 -15 Td (')}) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000618 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
695
%%EOF""".encode()
        with open(filename, 'wb') as f:
            f.write(pdf_content)
    return filename


def test_accuracy():
    """
    Test skill matching accuracy with known test cases.
    """
    print(f"\n{'='*60}")
    print("ACCURACY TEST")
    print(f"{'='*60}")
    
    # Test cases with expected results
    test_cases = [
        {
            "name": "Strong Match",
            "resume": "Skills: Python, Java, React, AWS, Docker, Kubernetes, PostgreSQL, REST APIs. 6 years experience. Built scalable microservices.",
            "job": "Required: Python, Java, React, AWS, Docker, 5+ years experience. Build REST APIs.",
            "expected_min_score": 50
        },
        {
            "name": "Moderate Match",
            "resume": "Skills: Python, Flask, MySQL, Linux. 3 years experience in backend development.",
            "job": "Required: Python, Java, React, AWS, Docker, 5+ years experience.",
            "expected_min_score": 30
        },
        {
            "name": "Weak Match",
            "resume": "Skills: Marketing, Sales, Excel, PowerPoint. 5 years in business development.",
            "job": "Required: Python, Java, React, AWS, Docker, 5+ years software engineering.",
            "expected_min_score": 0,
            "expected_max_score": 40
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases):
        print(f"\nTest {i+1}: {test['name']}")
        
        # Create temp resume PDF
        pdf_file = create_test_pdf(test["resume"], "temp_resume.pdf")
        
        try:
            with open(pdf_file, "rb") as f:
                response = requests.post(
                    f"{API_URL}/api/analyze",
                    files={"file": ("resume.pdf", f, "application/pdf")},
                    data={"jobDescriptionText": test["job"]},
                    timeout=120
                )
            
            if response.status_code == 200:
                data = response.json()
                score = data.get("matchScore", 0)
                
                # Check if score is in expected range
                min_expected = test.get("expected_min_score", 0)
                max_expected = test.get("expected_max_score", 100)
                passed = min_expected <= score <= max_expected
                
                results.append({
                    "name": test["name"],
                    "score": score,
                    "expected_range": f"{min_expected}-{max_expected}",
                    "passed": passed
                })
                
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"  Score: {score:.1f}% (expected: {min_expected}-{max_expected}%) {status}")
            else:
                print(f"  Error: {response.status_code}")
                results.append({"name": test["name"], "passed": False, "error": response.status_code})
                
        except Exception as e:
            print(f"  Exception: {str(e)[:50]}")
            results.append({"name": test["name"], "passed": False, "error": str(e)})
    
    # Summary
    passed = sum(1 for r in results if r.get("passed", False))
    total = len(results)
    accuracy = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n{'='*60}")
    print("ACCURACY RESULTS")
    print(f"{'='*60}")
    print(f"  Tests Passed: {passed}/{total}")
    print(f"  Accuracy:     {accuracy:.0f}%")
    print(f"{'='*60}")
    
    print("\n📝 RESUME BULLET POINT:")
    print(f"  'Achieved {accuracy:.0f}% accuracy on skill-matching test suite'")
    
    # Cleanup
    Path("temp_resume.pdf").unlink(missing_ok=True)
    
    return {"passed": passed, "total": total, "accuracy": accuracy}


def test_throughput(duration_seconds=30):
    """
    Measure requests per second throughput.
    """
    print(f"\n{'='*60}")
    print("THROUGHPUT TEST")
    print(f"{'='*60}")
    print(f"Running for {duration_seconds} seconds...")
    
    resume_file = create_sample_resume()
    
    start_time = time.time()
    requests_completed = 0
    errors = 0
    
    while time.time() - start_time < duration_seconds:
        try:
            with open(resume_file, 'rb') as f:
                response = requests.post(
                    f"{API_URL}/api/analyze",
                    files={"file": ("resume.pdf", f, "application/pdf")},
                    data={"jobDescriptionText": SAMPLE_JOB_DESCRIPTION},
                    timeout=120
                )
                if response.status_code == 200:
                    requests_completed += 1
                else:
                    errors += 1
        except:
            errors += 1
        
        # Progress indicator
        elapsed = time.time() - start_time
        print(f"\r  Progress: {elapsed:.0f}s / {duration_seconds}s | Completed: {requests_completed} | Errors: {errors}", end="")
    
    elapsed = time.time() - start_time
    throughput = requests_completed / elapsed
    
    print(f"\n\n{'='*60}")
    print("THROUGHPUT RESULTS")
    print(f"{'='*60}")
    print(f"  Duration:           {elapsed:.1f}s")
    print(f"  Requests Completed: {requests_completed}")
    print(f"  Errors:             {errors}")
    print(f"  Throughput:         {throughput:.2f} req/s")
    print(f"{'='*60}")
    
    print("\n📝 RESUME BULLET POINT:")
    print(f"  'AI service handles {throughput:.1f} requests/second sustained throughput'")
    
    return {"throughput": throughput, "completed": requests_completed, "errors": errors}


def test_health():
    """Quick health check of the service."""
    print(f"\n{'='*60}")
    print("HEALTH CHECK")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"  Status: ✓ Service is healthy")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"  Status: ✗ Unhealthy (HTTP {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  Status: ✗ Cannot connect to {API_URL}")
        print(f"  Make sure the AI service is running: python app.py")
        return False
    except Exception as e:
        print(f"  Status: ✗ Error: {e}")
        return False


def test_concurrency(num_concurrent=5, requests_per_thread=2):
    """
    Test concurrent request handling.
    Measures how many parallel requests the service can handle.
    """
    global total_processed
    total_processed = 0
    
    print(f"\n{'='*60}")
    print("CONCURRENCY TEST")
    print(f"{'='*60}")
    print(f"Running {num_concurrent} concurrent threads, {requests_per_thread} requests each...")
    print(f"Total requests: {num_concurrent * requests_per_thread}")
    
    resume_file = create_sample_resume()
    results = []
    errors = 0
    
    def make_request(thread_id, request_num):
        global total_processed
        try:
            with open(resume_file, 'rb') as f:
                file_content = f.read()
            
            start = time.time()
            response = requests.post(
                f"{API_URL}/api/analyze",
                files={"file": ("resume.pdf", file_content, "application/pdf")},
                data={"jobDescriptionText": SAMPLE_JOB_DESCRIPTION},
                timeout=120
            )
            elapsed = time.time() - start
            
            with request_counter:
                total_processed += 1
            
            if response.status_code == 200:
                print(f"  Thread {thread_id}, Request {request_num}: {elapsed:.2f}s ✓")
                return {"success": True, "time": elapsed, "thread": thread_id}
            else:
                print(f"  Thread {thread_id}, Request {request_num}: Error {response.status_code}")
                return {"success": False, "error": response.status_code}
        except Exception as e:
            print(f"  Thread {thread_id}, Request {request_num}: Exception - {str(e)[:30]}")
            return {"success": False, "error": str(e)}
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = []
        for thread_id in range(num_concurrent):
            for req_num in range(requests_per_thread):
                futures.append(executor.submit(make_request, thread_id + 1, req_num + 1))
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    
    total_time = time.time() - start_time
    
    # Calculate metrics
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    times = [r["time"] for r in successful]
    
    total_requests = num_concurrent * requests_per_thread
    success_rate = (len(successful) / total_requests) * 100 if total_requests > 0 else 0
    throughput = len(successful) / total_time if total_time > 0 else 0
    
    print(f"\n{'='*60}")
    print("CONCURRENCY RESULTS")
    print(f"{'='*60}")
    print(f"  Concurrent Threads:    {num_concurrent}")
    print(f"  Total Requests:        {total_requests}")
    print(f"  Successful:            {len(successful)}")
    print(f"  Failed:                {len(failed)}")
    print(f"  Success Rate:          {success_rate:.1f}%")
    print(f"  Total Time:            {total_time:.2f}s")
    print(f"  Throughput:            {throughput:.2f} req/s")
    
    if times:
        print(f"  Avg Response Time:     {statistics.mean(times):.2f}s")
        print(f"  Min Response Time:     {min(times):.2f}s")
        print(f"  Max Response Time:     {max(times):.2f}s")
    
    print(f"{'='*60}")
    
    print("\n📝 RESUME BULLET POINTS:")
    print(f"  'Handled {num_concurrent} concurrent users with {success_rate:.0f}% success rate'")
    print(f"  'Processed {len(successful)} resumes in {total_time:.1f}s under concurrent load'")
    if throughput > 0.5:
        print(f"  'Achieved {throughput:.1f} req/s throughput with {num_concurrent}-user concurrency'")
    
    # Cleanup
    Path("test_resume.pdf").unlink(missing_ok=True)
    
    return {
        "concurrent_users": num_concurrent,
        "total_requests": total_requests,
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": success_rate,
        "throughput": throughput,
        "total_time": total_time
    }


def run_all_tests():
    """Run all benchmark tests."""
    print("\n" + "="*60)
    print("   RESUME ANALYZER BENCHMARK SUITE")
    print("="*60)
    
    # Health check first
    if not test_health():
        print("\n⚠️  Service not available. Start it with: python app.py")
        return
    
    # Run tests
    latency_results = test_latency(num_requests=10)
    accuracy_results = test_accuracy()
    concurrency_results = test_concurrency(num_concurrent=3, requests_per_thread=2)
    
    # Final summary
    print("\n" + "="*60)
    print("   FINAL SUMMARY - METRICS FOR YOUR RESUME")
    print("="*60)
    
    if latency_results:
        print(f"\n📊 LATENCY:")
        print(f"   p50: {latency_results['p50']:.2f}s")
        print(f"   p95: {latency_results['p95']:.2f}s")
        print(f"   Resumes Processed: {latency_results['successful']}")
    
    if accuracy_results:
        print(f"\n🎯 ACCURACY:")
        print(f"   {accuracy_results['accuracy']:.0f}% on test suite")
    
    if concurrency_results:
        print(f"\n⚡ CONCURRENCY:")
        print(f"   {concurrency_results['concurrent_users']} concurrent users")
        print(f"   {concurrency_results['success_rate']:.0f}% success rate")
        print(f"   {concurrency_results['throughput']:.2f} req/s throughput")
    
    print("\n" + "="*60)
    print("   SUGGESTED RESUME BULLET POINTS")
    print("="*60)
    
    total_processed = (latency_results['successful'] if latency_results else 0) + \
                      (concurrency_results['successful'] if concurrency_results else 0) + \
                      (accuracy_results['total'] if accuracy_results else 0)
    
    print(f"\n✓ 'Processed {total_processed}+ resumes with {accuracy_results['accuracy']:.0f}% accuracy'")
    
    if concurrency_results and concurrency_results['success_rate'] >= 80:
        print(f"✓ 'Handled {concurrency_results['concurrent_users']} concurrent users with {concurrency_results['success_rate']:.0f}% success rate'")
    
    if latency_results:
        print(f"✓ 'Achieved p50 latency of {latency_results['p50']:.1f}s for end-to-end AI analysis'")
    
    error_rate = (latency_results['errors'] / latency_results['total_requests']) * 100 if latency_results else 0
    if error_rate < 5:
        print(f"✓ 'Maintained {100-error_rate:.0f}% success rate under load testing'")
    
    print("\n" + "="*60)
    
    # Cleanup
    Path("test_resume.pdf").unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark the Resume Analyzer AI Service")
    parser.add_argument("--test", choices=["latency", "accuracy", "throughput", "concurrency", "health", "all"], 
                        default="all", help="Which test to run")
    parser.add_argument("--requests", type=int, default=10, help="Number of requests for latency test")
    parser.add_argument("--duration", type=int, default=20, help="Duration in seconds for throughput test")
    parser.add_argument("--concurrent", type=int, default=3, help="Number of concurrent threads")
    
    args = parser.parse_args()
    
    if args.test == "health":
        test_health()
    elif args.test == "latency":
        if test_health():
            test_latency(args.requests)
    elif args.test == "accuracy":
        if test_health():
            test_accuracy()
    elif args.test == "throughput":
        if test_health():
            test_throughput(args.duration)
    elif args.test == "concurrency":
        if test_health():
            test_concurrency(num_concurrent=args.concurrent, requests_per_thread=2)
    else:
        run_all_tests()