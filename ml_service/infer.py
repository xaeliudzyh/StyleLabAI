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
    def __init__(self, cards, n_cls, emb_dim: int = 10):
        super().__init__()
        self.embs = nn.ModuleList([
            nn.Embedding(card + 1, min(emb_dim, (card + 1) // 2))
            for card in cards
        ])
        h = sum(e.embedding_dim for e in self.embs)
        self.layer_norm = nn.LayerNorm(h)
        self.dropout1   = nn.Dropout(p=0.30)
        self.fc1  = nn.Linear(h, 128)
        self.act1 = nn.ReLU()
        self.fc2  = nn.Linear(128, 256)
        self.act2 = nn.ReLU()
        self.dropout2 = nn.Dropout(p=0.30)
        self.fc_out = nn.Linear(256, n_cls)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        embs = [emb(x[:, i]) for i, emb in enumerate(self.embs)]
        x = torch.cat(embs, dim=1)
        x = self.layer_norm(x)
        x = self.dropout1(x)
        x = self.fc1(x)
        x = self.act1(x)
        x = self.fc2(x)
        x = self.act2(x)
        x = self.dropout2(x)
        x = self.fc_out(x)
        return x


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
