FROM python:3.12.3

WORKDIR /app

RUN apt-get update && \
  apt-get install -y \
  libgl1 \
  libglib2.0-0 \
  libsm6 \
  libxrender1 \
  libxext6 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

COPY best.pt .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]