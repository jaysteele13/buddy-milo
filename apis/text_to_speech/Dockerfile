FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    pkg-config \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Debug output: check CMakeLists.txt exists
RUN ls -l whisper.cpp && \
    cat whisper.cpp/CMakeLists.txt

# Build whisper.cpp
RUN rm -rf whisper.cpp/build && \
    cmake -S whisper.cpp -B whisper.cpp/build && \
    cmake --build whisper.cpp/build --config Release

# Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
