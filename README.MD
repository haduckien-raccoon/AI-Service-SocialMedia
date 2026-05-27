# AI Toxic Detection Service

Service FastAPI dùng để chấm điểm toxic cho văn bản tiếng Việt và tiếng Anh. Repo này được chuẩn hóa để chạy local, chạy trên VM bằng Docker Compose, và deploy cloud bằng Docker image/root `Dockerfile`.

## Runtime Overview

- App entrypoint: `main.py`
- Main endpoint: `POST /predict`
- Health endpoint: `GET /health`
- Runtime models:
  - `models/nlp_toxic_model_vi_final.pkl`
  - `models/nlp_toxic_model_en_final.pkl`

Docker image chỉ đóng gói các file runtime cần thiết. CSV train/test, notebook và artifact không dùng khi inference sẽ không đi vào image.

## Local Python Run

Yêu cầu:

- Python 3.12
- `pip`

Cài dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Chạy server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8082 --reload
```

Truy cập:

- API base: `http://127.0.0.1:8082`
- Swagger: `http://127.0.0.1:8082/docs`
- ReDoc: `http://127.0.0.1:8082/redoc`

## Docker Compose

Docker Compose là cách chạy được khuyến nghị cho local và VM vì build, run, port mapping và restart policy đều nằm trong một file cấu hình.

Chạy service:

```bash
docker compose up --build
```

Chạy background:

```bash
docker compose up --build -d
```

Xem logs:

```bash
docker compose logs -f api
```

Dừng service:

```bash
docker compose down
```

Tùy chỉnh port bằng file `.env` ở root repo:

```bash
PORT=8082
HOST_PORT=8082
```

`PORT` là port app lắng nghe bên trong container. `HOST_PORT` là port máy host expose ra ngoài. File `.env.example` là template để team thống nhất cấu hình.

## Docker CLI

Build image từ root repo:

```bash
docker build -t ai-service-socialmedia:latest .
```

Run local với port mặc định:

```bash
docker run --rm -p 8082:8082 ai-service-socialmedia:latest
```

Run theo kiểu cloud với `PORT` inject từ platform:

```bash
docker run --rm -e PORT=8000 -p 8000:8000 ai-service-socialmedia:latest
```

## API Verification

Kiểm tra health endpoint:

```bash
curl http://127.0.0.1:8082/health
```

Kết quả mong đợi:

```json
{"status":"ok"}
```

Kiểm tra model tiếng Việt:

```bash
curl -X POST "http://127.0.0.1:8082/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"mày ngu quá\",\"lang\":\"vi\"}"
```

Kiểm tra model tiếng Anh:

```bash
curl -X POST "http://127.0.0.1:8082/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"you are stupid\",\"lang\":\"en\"}"
```

Response mẫu:

```json
{
  "score": 0.9821,
  "lang": "vi"
}
```

`score` càng gần `1` thì nội dung càng toxic. `lang` mặc định là `vi` nếu request không truyền.

## Cloud Deployment Notes

- Dockerfile canonical nằm ở root repo.
- `compose.yaml` dùng cho local và VM chạy Docker Compose. Với PaaS/container platform, ưu tiên deploy bằng image hoặc root `Dockerfile` tùy provider.
- Container sẽ đọc `PORT` nếu platform inject biến môi trường này. Nếu không có, app dùng mặc định `8082`.
- Health probe nên trỏ vào `GET /health`.
- Build context đã được tối giản bằng `.dockerignore` để tránh đẩy `venv/`, dữ liệu train/test và artifact không cần thiết lên builder.

## Troubleshooting

- `FileNotFoundError` khi start container:
  - Kiểm tra hai file model final còn tồn tại trong `models/`.
- Container chạy nhưng không truy cập được:
  - Kiểm tra mapping port host/container và giá trị `PORT`.
- Docker Compose không đọc đúng port:
  - Kiểm tra file `.env`, giá trị `HOST_PORT`, và chạy lại `docker compose up --build`.
- Docker build quá chậm hoặc context quá lớn:
  - Kiểm tra `.dockerignore` có còn loại trừ `venv/`, `__pycache__/`, CSV và notebook hay không.
