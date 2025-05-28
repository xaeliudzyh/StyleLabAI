import json
from pathlib import Path

import requests

# 1) Загрузим JSON из sample.json
SAMPLE = Path(__file__).with_suffix('.json')  # sample.json лежит рядом с тестом
with open(SAMPLE, encoding="utf-8") as f:
    data = json.load(f)

# 2) Пошлём запрос на /infer
resp = requests.post("http://127.0.0.1:9000/infer", json=data)
print("Status:", resp.status_code)
print("Response:", resp.text)
