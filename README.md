# StyleLab: AI-powered Hairstyle Recommendations

StyleLab is a cloud-based application that suggests best hairstyles based on user profile data using our custom PyTorch model **StyleNet**.

---

## Features

* **Smart Recommendations**: StyleNet predicts and ranks hairstyles with confidence scores.
* **REST API**: JWT authentication, endpoints for users, clients, barbershops, surveys, and recommendations.
* **Cloud Infrastructure**: PostgreSQL for structured data, Object Storage for images, deployed via Terraform on Yandex Cloud.
* **Scalable**: Containerized services on Kubernetes with auto-scaling and CI/CD pipelines.

---

## Quick Start

1. **Clone repository**

   ```bash
   git clone https://github.com/xaeliudzyh/StyleLab.git
   cd StyleLab
   ```
   
2. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run inference service**
   ```bash
   uvicorn ml_service.main:app --reload --host 0.0.0.0 --port 9000
   ```

4. **Run main API**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Test recommendation**
   ```bash
   python test_recommend.py
   ```

---
## Model Metrics
![Model Metrics](docs/metrics/loss)
![Model Metrics](docs/metrics/acc1)
![Model Metrics](docs/metrics/acc3)
*StyleNet performance on test data.*

---
## Project Structure
```

StyleLab/
├── app/            # Main FastAPI backend
├── ml\_service/     # FastAPI inference service + model artifacts
├── iac/            # Terraform configs for Yandex Cloud
├── docs/           # Reports, metrics image
├── tests/          # Unit tests
└── README.md

```

---
## Work is not done yet. Still in progress...

---
*© 2025 StyleLab*
