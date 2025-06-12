from ml_service.main import app
from fastapi.testclient import TestClient
import json, pathlib

SAMPLE = pathlib.Path(__file__).with_suffix('.json')
data = json.loads(SAMPLE.read_text(encoding="utf-8"))

client = TestClient(app)

def test_infer():
    r = client.post("/infer", json=data)
    assert r.status_code == 200
    assert "predictions" in r.json()
    assert len(r.json()["predictions"]) == 3
