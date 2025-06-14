from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib, torch
import torch.nn.functional as F
from ml_service.infer import predict_top3

# Схема входа для /infer
class Features(BaseModel):
    Возраст: str
    Форма_Лица: str = Field(..., alias="Форма Лица")
    Структура_волос: str = Field(..., alias="Структура волос")
    Густота_волос: str = Field(..., alias="Густота волос")
    Длина_волос: str = Field(..., alias="Длина волос")
    Цвет_волос: str = Field(..., alias="Цвет волос")
    Среднее_время: str = Field(..., alias="Среднее время на укладку(минут в день)")
    Образ_жизни: str = Field(..., alias="Образ жизни")
    Стиль: str
    Телосложение: str = Field(..., alias="Телосложение")
    Стиль_одежды: str = Field(..., alias="Стиль одежды")
    Использование_средств: str = Field(..., alias="Использование укладочных средств")
    Тип_укладки: str = Field(..., alias="Тип укладки")
    Использование_фена: str = Field(..., alias="Использование фена")

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"

app = FastAPI(title="StyleNet Inference")

@app.post("/infer")
def infer(features: Features):
    try:
        # используем нашу функцию infer.py
        result = predict_top3(features.model_dump(by_alias=True))
        return {"predictions": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))