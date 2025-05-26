from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ml_service.infer import predict_top3
from pydantic import BaseModel, Field

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

app = FastAPI(title="StyleNet inference")

@app.post("/infer")
def infer(features: Features):
    try:
        result = predict_top3(features.dict(by_alias=True))
        return {"predictions": result}
    except Exception as e:
        raise HTTPException(400, detail=str(e))
