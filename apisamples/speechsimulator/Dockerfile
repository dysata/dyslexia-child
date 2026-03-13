# apisamples/speechsimulator/Dockerfile
FROM python:3.10.19-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for WebRTC/av)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Для сборки PyAV и других C-расширений
#    build-essential \
#    pkg-config \
#    \
    # FFmpeg и библиотеки для av/aiortc
    ffmpeg \
#    libavcodec-dev \
#    libavformat-dev \
#    libavdevice-dev \
#    libavfilter-dev \
#    libswscale-dev \
#    libswresample-dev \
    \
    # Для aiortc (WebRTC)
#    libglib2.0-dev \
#    libopus-dev \
#    libvpx-dev \
    \
    # Утилиты для healthcheck и отладки
#    curl \
#    \
    # Очистка кэша для уменьшения размера образа
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

#RUN execstack -c /usr/local/lib/python3.10/site-packages/torch/lib/*.so || true

# Create non-root user for security
RUN useradd -m -u 1000 appuser && mkdir -p /app/storage && chown -R appuser:appuser /app
USER appuser

# Expose the port your app will listen on (HTTP, not HTTPS!)
EXPOSE 8000

# Health check endpoint (add /health to your aiohttp app if not present)
#HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command: run on HTTP, port 8000, bind to 0.0.0.0
# Your app should accept these args or use environment variables
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000"]
