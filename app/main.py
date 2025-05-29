import httpx
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ml_service.infer import predict_top3
from ml_service.main import Features
from .db import SessionLocal
from . import crud, schemas

app = FastAPI(title="Hairstyle recommender – API v0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/clients", response_model=schemas.ClientOut, status_code=201)
def create_client(payload: schemas.ClientCreate, db: Session = Depends(get_db)):
    return crud.create_client(db, payload)


@app.get("/clients/{cid}", response_model=schemas.ClientOut)
def read_client(cid: int, db: Session = Depends(get_db)):
    obj = crud.get_client(db, cid)
    if not obj:
        raise HTTPException(404, "Client not found")
    return obj


@app.delete("/clients/{cid}", status_code=204)
def remove_client(cid: int, db: Session = Depends(get_db)):
    if not crud.delete_client(db, cid):
        raise HTTPException(404, "Client not found")


class RecommendRequest(Features):
    client_id: int = Field(..., alias="client_id")
    top_k:      int = 3

app = FastAPI()

@app.post("/recommend")
async def recommend(req: RecommendRequest):
    payload = req.dict(by_alias=True, exclude_none=True)
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post("http://127.0.0.1:9000/infer", json=payload)
            r.raise_for_status()
            preds = r.json().get("predictions", [])
    except (httpx.HTTPError, httpx.ConnectError):
        # если ML-сервис не доступен (в CI), делаем локально
        preds = predict_top3(payload)
    return {"recommendations": preds}
