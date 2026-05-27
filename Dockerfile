FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app main.py ./main.py
COPY --chown=app:app models/nlp_toxic_model_vi_final.pkl ./models/nlp_toxic_model_vi_final.pkl
COPY --chown=app:app models/nlp_toxic_model_en_final.pkl ./models/nlp_toxic_model_en_final.pkl

USER app

EXPOSE 8082

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import os, urllib.request; port = os.environ.get('PORT', '8082'); urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=3)"

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8082}"]
