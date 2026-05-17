# AI Toxic Detection Service

API phát hiện nội dung độc hại (toxic text detection) hỗ trợ tiếng Việt và tiếng Anh bằng `FastAPI`.

## Cấu trúc thư mục

```bash
ai_services/
├── docker/
├── models/
│   ├── nlp_toxic_model_vi_final.pkl
│   └── nlp_toxic_model_en_final.pkl
├── main.py
├── requirements.txt
├── README.MD
├── venv/
└── __pycache__/
```

---

# Yêu cầu môi trường

* Python >= 3.9
* pip
* virtualenv (khuyến nghị)

---

# Cài đặt

## 1. Clone project

```bash
git clone <your-repository>
cd ai_services
```

---

## 2. Tạo virtual environment

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 3. Cài dependencies

```bash
pip install -r requirements.txt
```

---

# Chạy server

```bash
uvicorn main:app --reload
uvicorn main:app --reload --host 0.0.0.0 --port 8081
```

Server sẽ chạy tại:

```bash
http://127.0.0.1:8081
```

Swagger Docs:

```bash
http://127.0.0.1:8081/docs
```

Redoc:

```bash
http://127.0.0.1:8081/redoc
```

---

# API Usage

## Endpoint

```http
POST /predict
```

---

## Request Body

### Tiếng Việt

```json
{
  "text": "mày ngu quá",
  "lang": "vi"
}
```

### Tiếng Anh

```json
{
  "text": "you are stupid",
  "lang": "en"
}
```

---

# Response

```json
{
  "score": 0.9821,
  "lang": "vi"
}
```

---

# Ý nghĩa kết quả

| Score | Ý nghĩa                  |
| ----- | ------------------------ |
| gần 0 | Nội dung an toàn         |
| gần 1 | Nội dung độc hại / toxic |

---

# Chạy bằng cURL

## Vietnamese

```bash
curl -X POST "http://127.0.0.1:8081/predict" \
-H "Content-Type: application/json" \
-d '{"text":"mày ngu quá","lang":"vi"}'
```

## English

```bash
curl -X POST "http://127.0.0.1:8081/predict" \
-H "Content-Type: application/json" \
-d '{"text":"you are stupid","lang":"en"}'
```

---

# Source Code

## main.py

```python
from fastapi import FastAPI
import joblib

app = FastAPI()

model_vi = joblib.load("models/nlp_toxic_model_vi_final.pkl")
model_en = joblib.load("models/nlp_toxic_model_en_final.pkl")


@app.post("/predict")
def predict(data: dict):
    text = data["text"]
    lang = data.get("lang", "vi")

    if lang == "en":
        model = model_en
    else:
        model = model_vi

    proba = model.predict_proba([text])[0][1]

    return {
        "score": float(proba),
        "lang": lang
    }
```

---

# Docker (tuỳ chọn)

## Build image

```bash
docker build -t toxic-api .
```

## Run container

```bash
docker run -p 8081:8081 toxic-api
```

---

# Ghi chú

* `lang="vi"` là mặc định.
* Model được load khi server khởi động.
* API trả về xác suất toxic (`score`) thay vì label nhị phân.
* Các model `.pkl` cần tồn tại trong thư mục `models/`.

---

# Author

Developed using:

* Python
* FastAPI
* scikit-learn
* joblib
