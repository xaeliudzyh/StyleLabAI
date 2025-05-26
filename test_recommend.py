import json, requests

# берём sample.json из ml_service
with open("ml_service/api_test/sample.json", encoding="utf-8") as f:
    data = json.load(f)
data["client_id"] = 1
data["top_k"] = 3

r = requests.post("http://127.0.0.1:8000/recommend", json=data)
print(r.status_code, r.json())
