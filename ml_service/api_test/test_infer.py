import json
import requests

# 1) Загрузим JSON из sample.json
with open("sample.json", encoding="utf-8") as f:
    data = json.load(f)

# 2) Пошлём запрос на /infer
resp = requests.post("http://127.0.0.1:9000/infer", json=data)
print("Status:", resp.status_code)
print("Response:", resp.text)
