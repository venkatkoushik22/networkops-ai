FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV NETWORKOPS_PUBLIC_DEMO=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && `
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["sh", "-c", "uvicorn backend.main:app --host 127.0.0.1 --port 8000 & exec streamlit run dashboard/app.py --server.address=0.0.0.0 --server.port=7860 --server.headless=true --browser.gatherUsageStats=false"]
