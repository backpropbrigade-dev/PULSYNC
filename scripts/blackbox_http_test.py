import urllib.request
import json
import sqlite3
import time

BASE_URL = "http://localhost:8000"
TEST_ANON_ID = "blackbox_anon_id_999"

def make_request(method, path, body=None, headers=None):
    if headers is None:
        headers = {}
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode('utf-8') if body is not None else None
    if body is not None and 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            res_body = response.read().decode('utf-8')
            try:
                json_data = json.loads(res_body)
            except Exception:
                json_data = res_body
            return status, json_data, dict(response.headers)
    except urllib.error.HTTPError as e:
        res_body = e.read().decode('utf-8')
        try:
            json_data = json.loads(res_body)
        except Exception:
            json_data = res_body
        return e.code, json_data, dict(e.headers)

print("==================================================")
print("PULSYNC BLACK-BOX HTTP API INTEGRATION TESTS")
print("==================================================")

# 1. Health
st, data, _ = make_request("GET", "/api/health")
print(f"[1] GET /api/health -> Status: {st}, Response: {data}")

# 2. Auth me
st, data, _ = make_request("GET", "/api/auth/me")
print(f"[2] GET /api/auth/me -> Status: {st}, User ID: {data.get('user', {}).get('id') if isinstance(data, dict) else data}")

# 3. Promotions
st, data, _ = make_request("GET", "/api/promotions")
print(f"[3] GET /api/promotions -> Status: {st}, Banners count: {len(data.get('banners', [])) if isinstance(data, dict) else 0}")

# 4. Sports
st, data, _ = make_request("GET", "/api/sports")
print(f"[4] GET /api/sports -> Status: {st}, Sports count: {len(data.get('sports', [])) if isinstance(data, dict) else 0}")

# 5. Events (sport=all&day=all)
st, data, _ = make_request("GET", "/api/events?sport=all&day=all")
print(f"[5] GET /api/events?sport=all&day=all -> Status: {st}, Total: {data.get('total') if isinstance(data, dict) else 0}")

# 6. Events (sport=all&day=today)
st, data, _ = make_request("GET", "/api/events?sport=all&day=today")
print(f"[6] GET /api/events?sport=all&day=today -> Status: {st}, Total: {data.get('total') if isinstance(data, dict) else 0}")

# 7. POST /api/sessions First Call
st1, sess1, _ = make_request("POST", "/api/sessions", body={"anonymous_user_id": TEST_ANON_ID})
sid1 = sess1.get("session_id") if isinstance(sess1, dict) else None
uid1 = sess1.get("user_id") if isinstance(sess1, dict) else None
print(f"[7] POST /api/sessions (First Call) -> Status: {st1}, Session ID: {sid1}, User ID: {uid1}")

# 8. POST /api/sessions Second Call (Same anonymous_id)
st2, sess2, _ = make_request("POST", "/api/sessions", body={"anonymous_user_id": TEST_ANON_ID})
sid2 = sess2.get("session_id") if isinstance(sess2, dict) else None
uid2 = sess2.get("user_id") if isinstance(sess2, dict) else None
print(f"[8] POST /api/sessions (Second Call) -> Status: {st2}, Session ID: {sid2}, User ID: {uid2}")

# 9. Ingest Event
event_payload = {
    "user_id": uid1,
    "event_type": "comparison",
    "page": "comparison",
    "action": "inspect_teams",
    "sport": "Football",
    "match_id": "match_rma_bar"
}
st, intel, _ = make_request("POST", f"/api/sessions/{sid1}/events", body=event_payload)
print(f"[9] POST /api/sessions/{sid1}/events -> Status: {st}, Intent: {intel.get('intent') if isinstance(intel, dict) else intel}")

# 10. Get Intelligence
st, intel2, _ = make_request("GET", f"/api/sessions/{sid1}/intelligence")
print(f"[10] GET /api/sessions/{sid1}/intelligence -> Status: {st}, Intent: {intel2.get('intent') if isinstance(intel2, dict) else intel2}")

# 11. Get Recommendations
st, recs_resp, _ = make_request("GET", f"/api/recommendations/{sid1}")
recs = recs_resp.get("recommendations", []) if isinstance(recs_resp, dict) else []
first_rec = recs[0] if recs else {}
print(f"[11] GET /api/recommendations/{sid1} -> Status: {st}, Recs Count: {len(recs)}, Top Rec: {first_rec.get('title')}")

# 12. Submit Feedback
if first_rec.get("content_id"):
    fb_payload = {"content_id": first_rec.get("content_id"), "feedback_type": "clicked"}
    st, fb_res, _ = make_request("POST", f"/api/recommendations/{sid1}/feedback", body=fb_payload)
    print(f"[12] POST /api/recommendations/{sid1}/feedback -> Status: {st}, Result: {fb_res}")

# 13. Edge Cases & Robustness
# CORS OPTIONS
st, _, headers = make_request("OPTIONS", "/api/sessions", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
print(f"[13a] OPTIONS /api/sessions (CORS Preflight) -> Status: {st}")

# Unknown Session
st, unk_res, _ = make_request("GET", "/api/sessions/non_existent_session_id_999/intelligence")
print(f"[13b] GET /api/sessions/non_existent/intelligence -> Status: {st} (Expected 404)")

# Repeated Identical Event
st, intel_rep, _ = make_request("POST", f"/api/sessions/{sid1}/events", body=event_payload)
print(f"[13c] Repeated Identical Event -> Status: {st}, Friction Level: {intel_rep.get('friction_level') if isinstance(intel_rep, dict) else intel_rep}")

# 14. Database Persistence Verification
print("\n==================================================")
print("DATABASE PERSISTENCE VERIFICATION")
print("==================================================")
conn = sqlite3.connect("pulsync.db")
cur = conn.cursor()

# Query user rows for TEST_ANON_ID
cur.execute("SELECT id, anonymous_id, segment, created_at FROM users WHERE anonymous_id = ?", (TEST_ANON_ID,))
user_rows = cur.fetchall()
print(f"Users found for anonymous_id='{TEST_ANON_ID}': {len(user_rows)}")
for u in user_rows:
    print(f"  User record -> ID: {u[0]}, anonymous_id: {u[1]}, Segment: {u[2]}")

# Query session rows for user
if user_rows:
    target_uid = user_rows[0][0]
    cur.execute("SELECT id, user_id, started_at, status FROM sessions WHERE user_id = ?", (target_uid,))
    sess_rows = cur.fetchall()
    print(f"Sessions found for user_id='{target_uid}': {len(sess_rows)}")
    for s in sess_rows:
        print(f"  Session record -> ID: {s[0]}, user_id: {s[1]}, Status: {s[3]}")

conn.close()
