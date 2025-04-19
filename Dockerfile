FROM python:3.13-slim

# Install system dependencies required for Argos Translate
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    libprotobuf-dev \
    protobuf-compiler \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
COPY static/ static/
RUN pip install --no-cache-dir -r requirements.txt

COPY translate_api.py ./
COPY translation_models.py ./

# Install Argos models during build
RUN python -c "import translation_models; translation_models.install()"

CMD ["uvicorn", "translate_api:app", "--host", "0.0.0.0", "--port", "8080"]
