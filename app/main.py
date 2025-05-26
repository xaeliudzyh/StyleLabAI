import httpx
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
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

@app.post("/recommend")
async def recommend(req: RecommendRequest):
    # 1) Собираем payload в виде словаря по alias
    payload = req.dict(by_alias=True, exclude_none=True)
    # 2) Отправляем на локальный ML-сервис
    async with httpx.AsyncClient() as client:
        r = await client.post("http://127.0.0.1:9000/infer", json=payload)
    if r.status_code != 200:
        raise HTTPException(r.status_code, detail=f"ML error: {r.text}")
    preds = r.json()["predictions"]
    return {"recommendations": preds}
