from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import psutil
import os
import re
import unicodedata
from pyvi import ViTokenizer

app = FastAPI(
    title="Toxic Content Moderation API",
    description="API kiểm duyệt nội dung độc hại sử dụng mô hình học máy (Việt/Anh)",
    version="1.0.0"
)

# ==========================================
# 1. ĐỊNH NGHĨA KHUÔN DỮ LIỆU ĐẦU VÀO (PYDANTIC)
# ==========================================
class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Nội dung văn bản cần kiểm duyệt", examples=["Na là một người học dốt"])
    lang: str = Field("vi", description="Ngôn ngữ của văn bản ('vi' hoặc 'en')", examples=["vi"])

class PredictResponse(BaseModel):
    score: float = Field(..., description="Xác suất độc hại (từ 0.0 đến 1.0)")
    label: int = Field(..., description="Nhãn dự đoán (0: An toàn, 1: Độc hại)")
    lang: str

# ==========================================
# 2. TÁI ĐỊNH NGHĨA HÀM TIỀN XỬ LÝ (NLP PREPROCESSING)
# Bắt buộc phải trùng khớp 100% với lúc Train Model
# ==========================================
def preprocess_vietnamese(text: str) -> str:
    if not text: return ""
    text = str(text).lower()
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'http\S+|@\S+|#\S+', ' ', text)
    text = re.sub(r'([a-z])\1+', r'\1\1', text)
    text = re.sub(r'[^\w\s!?]', ' ', text)
    text = ViTokenizer.tokenize(text.strip())
    return text

def preprocess_english(text: str) -> str:
    if not text: return ""
    text = str(text).lower()
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'http\S+|@\S+|#\S+', ' ', text)
    text = re.sub(r'([a-z])\1+', r'\1\1', text)
    text = re.sub(r'[^\w\s!?]', ' ', text)
    return text.strip()

# ==========================================
# 3. LOAD MODELS (Chạy 1 lần duy nhất khi khởi động API)
# ==========================================
MODEL_VI_PATH = "models/nlp_toxic_model_vi_final.pkl"
MODEL_EN_PATH = "models/nlp_toxic_model_en_final.pkl"

try:
    model_vi = joblib.load(MODEL_VI_PATH)
    model_en = joblib.load(MODEL_EN_PATH)
    print("✅ Đã tải thành công các mô hình kiểm duyệt.")
except Exception as e:
    print(f"❌ Lỗi nghiêm trọng khi tải mô hình: {e}")
    raise RuntimeError(f"Không thể khởi động API do thiếu file model: {e}")

# ==========================================
# 4. MEMORY MONITORING HELPER
# ==========================================
def get_memory_usage():
    process = psutil.Process(os.getpid())
    mem_bytes = process.memory_info().rss
    return {
        "memory_mb": round(mem_bytes / (1024 ** 2), 2),
        "memory_gb": round(mem_bytes / (1024 ** 3), 3)
    }

# ==========================================
# 5. ENDPOINTS
# ==========================================
@app.get("/health")
def health():
    return {"status": "ok", **get_memory_usage()}

@app.get("/memory")
def memory():
    return get_memory_usage()

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """
    Dự đoán mức độ độc hại của văn bản theo ngôn ngữ chỉ định.
    - **text**: Văn bản thô cần kiểm tra.
    - **lang**: 'vi' (mặc định) hoặc 'en'.
    """
    raw_text = request.text
    lang = request.lang.lower().strip()

    # Chọn mô hình và áp dụng tiền xử lý tương ứng
    if lang == "en":
        model = model_en
        cleaned_text = preprocess_english(raw_text)
    elif lang == "vi":
        model = model_vi
        cleaned_text = preprocess_vietnamese(raw_text)
    else:
        raise HTTPException(status_code=400, detail="Hệ thống hiện tại chỉ hỗ trợ mã ngôn ngữ 'vi' hoặc 'en'.")

    try:
        # Thực hiện dự đoán trên văn bản ĐÃ QUA TIỀN XỬ LÝ
        # model.predict_proba nhận vào một mảng/danh sách các văn bản
        proba_matrix = model.predict_proba([cleaned_text])
        proba_toxic = float(proba_matrix[0][1])
        
        # Ngưỡng phân loại mặc định (Có thể điều chỉnh thành 0.3-0.4 nếu muốn tăng Recall lớp Toxic)
        label = 1 if proba_toxic >= 0.5 else 0

        return PredictResponse(
            score=proba_toxic,
            label=label,
            lang=lang
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi trong quá trình xử lý suy diễn: {str(e)}")