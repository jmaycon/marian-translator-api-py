FROM python:3.10-slim

# Install system dependencies required for sentencepiece
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    libprotobuf-dev \
    protobuf-compiler \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY translate_api.py /app/translate_api.py

CMD ["uvicorn", "translate_api:app", "--host", "0.0.0.0", "--port", "8080"]
