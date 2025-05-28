from fastapi.testclient import TestClient
from app.main import app
import json, pathlib

client = TestClient(app)

DATA = {
    # тот же словарь анкеты
    "client_id": 1,
    "top_k": 3
}

def test_recommend():
    r = client.post("/recommend", json=DATA)
    assert r.status_code == 200
    assert len(r.json()["recommendations"]) == 3
