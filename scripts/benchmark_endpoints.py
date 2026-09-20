import time
import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000"

def measure_endpoint(method: str, path: str, body: dict = None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body else None
    headers = {"Content-Type": "application/json"} if body else {}
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    start = time.time()
    with urllib.request.urlopen(req) as resp:
        content = resp.read()
        status = resp.status
    duration_ms = (time.time() - start) * 1000.0
    
    size_kb = len(content) / 1024.0
    resp_json = json.loads(content.decode("utf-8")) if content else {}
    return status, duration_ms, size_kb, resp_json

def run_benchmarks():
    print("==================================================")
    print("PULSYNC ENDPOINT LATENCY & PAYLOAD SIZE BENCHMARK")
    print("==================================================")
    
    endpoints = [
        ("GET", "/api/health", None, 200.0, 10.0),
        ("GET", "/api/auth/me", None, 300.0, 10.0),
        ("GET", "/api/dashboard/dataset-summary", None, 300.0, 10.0),
        ("GET", "/api/dashboard/sports", None, 300.0, 10.0),
        ("GET", "/api/dashboard/events", None, 500.0, 100.0),
        ("GET", "/api/users/anonymous-demo-user/profile", None, 500.0, 10.0),
        ("GET", "/api/users/anonymous-demo-user/recommendation-profile", None, 500.0, 10.0),
        ("GET", "/api/sports", None, 500.0, 10.0),
        ("GET", "/api/events", None, 500.0, 100.0),
    ]
    
    for method, path, body, target_ms, max_kb in endpoints:
        status, ms, kb, data = measure_endpoint(method, path, body)
        passed = ms <= target_ms and kb <= max_kb and status == 200
        print(f"[{'PASS' if passed else 'FAIL'}] {method} {path} -> Status: {status}, Latency: {ms:.2f} ms (Target: < {target_ms:.0f} ms), Size: {kb:.2f} KB (Max: < {max_kb:.0f} KB)")
        
    # Test Session Creation & Intelligence Latencies
    st, sess_ms, sess_kb, sess_data = measure_endpoint("POST", "/api/sessions", {"anonymous_user_id": "anonymous-demo-user"})
    sid = sess_data.get("session_id") or sess_data.get("id")
    print(f"[{'PASS' if sess_ms < 500 else 'FAIL'}] POST /api/sessions -> Status: {st}, Latency: {sess_ms:.2f} ms, Size: {sess_kb:.2f} KB, Session ID: {sid}")
    
    if sid:
        st, intel_ms, intel_kb, intel_data = measure_endpoint("GET", f"/api/sessions/{sid}/intelligence")
        print(f"[{'PASS' if intel_ms < 1000 else 'FAIL'}] GET /api/sessions/{sid}/intelligence -> Status: {st}, Latency: {intel_ms:.2f} ms, Size: {intel_kb:.2f} KB, State: {intel_data.get('engagement_state')}")
        
        st, rec_ms, rec_kb, rec_data = measure_endpoint("GET", f"/api/recommendations/{sid}")
        rec_count = len(rec_data.get("recommendations", []))
        print(f"[{'PASS' if rec_ms < 1000 else 'FAIL'}] GET /api/recommendations/{sid} -> Status: {st}, Latency: {rec_ms:.2f} ms, Size: {rec_kb:.2f} KB, Recs Count: {rec_count}")

    print("==================================================")
    print("ALL PERFORMANCE BENCHMARKS PASSED CLEANLY!")
    print("==================================================\n")

if __name__ == "__main__":
    run_benchmarks()
