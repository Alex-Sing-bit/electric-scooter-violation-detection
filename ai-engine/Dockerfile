FROM python:3.12-bookworm

RUN apt-get update --fix-missing && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxcb1 \
    libx11-6 \
    libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/src
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]