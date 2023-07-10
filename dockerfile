FROM python:3.10-slim

WORKDIR /app

COPY bot-requirements.txt .

RUN pip install --upgrade pip setuptools

RUN pip install --no-cache-dir -r bot-requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]

