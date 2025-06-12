import torch, joblib, torch.nn.functional as F
from pathlib import Path
import torch
import torch.nn as nn
import joblib
DEVICE = "cpu"            # менять на "cuda" при необходимости

# ——— загрузка артефактов ———
ART_DIR = Path(__file__).parent / "artifacts"
checkpoint = torch.load(ART_DIR / "stylenet.pt", map_location=DEVICE)
# в нём ваши веса и, возможно, список cardinalities
state_dict = checkpoint.get("state_dict", checkpoint)


# карта категориальных столбцов (тот же порядок, что при обучении!)
cat_cols = ['Возраст',
 'Форма Лица',
 'Структура волос',
 'Густота волос',
 'Длина волос',
 'Цвет волос',
 'Среднее время на укладку(минут в день)',
 'Образ жизни',
 'Стиль',
 'Телосложение',
 'Стиль одежды',
 'Использование укладочных средств',
 'Тип укладки',
 'Использование фена']

# размерности категорий — читаем из encoder
ord_enc = joblib.load(ART_DIR / "feature_encoder.joblib")
n_classes = len(joblib.load(ART_DIR / "label_encoder.joblib").classes_)

cards      = checkpoint.get("cardinalities", [len(c) for c in ord_enc.categories_])

# ——— модель ———
import torch
import torch.nn as nn

class StyleNet(nn.Module):
    def __init__(self, cards, n_cls, emb_dim=10):
        super().__init__()
        self.em = nn.ModuleList(
            [nn.Embedding(c+1, min(emb_dim, (c+1)//2)) for c in cards]
        )
        h = sum(e.embedding_dim for e in self.em)

        self.net = nn.Sequential(
            nn.LayerNorm(h),
            nn.Dropout(0.30),
            nn.Linear(h, 128), nn.ReLU(),
            nn.Linear(128, 256), nn.ReLU(),
            nn.Dropout(0.30),
            nn.Linear(256, n_cls)
        )

    def forward(self, x):
        x = torch.cat([e(x[:, i]) for i, e in enumerate(self.em)], 1)
        return self.net(x)


model = StyleNet(cards, n_classes)
model.load_state_dict(state_dict)
model.eval().to(DEVICE)

def preprocess(payload: dict):
    vals = [payload[col] for col in cat_cols]
    X = ord_enc.transform([vals])
    return torch.as_tensor(X, dtype=torch.long, device=DEVICE)

def predict_top3(payload: dict):
    with torch.no_grad():
        X = preprocess(payload)
        probs = F.softmax(model(X), dim=1).cpu().numpy().ravel()
    top = probs.argsort()[-3:][::-1]
    lbl_enc = joblib.load(ART_DIR / "label_encoder.joblib")
    return [
        {"style": lbl_enc.inverse_transform([i])[0],
         "prob": float(probs[i])}
        for i in top
    ]
