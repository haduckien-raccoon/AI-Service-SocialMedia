# ================================
# AI SERVICE - FASTAPI DOCKER
# ================================

FROM python:3.10-slim

# tránh .pyc + buffer log
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ================================
# install dependencies
# ================================
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ================================
# copy source code
# ================================
COPY . .

# ================================
# expose port
# ================================
EXPOSE 8081

# ================================
# run production server
# ================================
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
