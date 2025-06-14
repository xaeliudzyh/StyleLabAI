import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# load the same sample you use in ml_service tests
sample_path = Path(__file__).parent / "ml_service" / "api_test" / "test_infer.json"
payload = json.loads(sample_path.read_text(encoding="utf-8"))

# now add the two extra fields
payload["client_id"] = 1
payload["top_k"]      = 3

def test_recommend():
    r = client.post("/recommend", json=payload)
    assert r.status_code == 200
    assert len(r.json()["recommendations"]) == 3
