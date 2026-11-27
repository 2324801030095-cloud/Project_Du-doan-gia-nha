# Dịch vụ mô hình (FastAPI). Build từ thư mục gốc đề tài: cần src/, models/, dataset/processed/
FROM python:3.14-slim
WORKDIR /app
# LightGBM cần thư viện OpenMP
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
COPY api/requirements.txt api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt
COPY src ./src
COPY models ./models
# CSV căn hộ là phần mở rộng: .dockerignore chỉ cho 2 tệp đã xử lý vào ngữ cảnh, tệp nào không có thì bỏ qua
COPY dataset/processed ./dataset/processed/
COPY api ./api
RUN useradd -r api && chown -R api /app
USER api
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=40s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uvicorn", "main:app", "--app-dir", "api", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
