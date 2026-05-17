from fastapi import FastAPI
import joblib

app = FastAPI()

model_vi = joblib.load("models/nlp_toxic_model_vi_final.pkl")

model_en = joblib.load("models/nlp_toxic_model_en_final.pkl")


# ==========================================
# PREDICT
# ==========================================
@app.post("/predict")
def predict(data: dict):
    text = data["text"]
    lang = data.get("lang", "vi")  # default vi

    if lang == "en":
        model = model_en
    else:
        model = model_vi

    proba = model.predict_proba([text])[0][1]

    return {
        "score": float(proba),
        "lang": lang
    }
