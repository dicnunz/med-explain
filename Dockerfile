FROM python:3.11-slim

# Install tesseract and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app
COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
