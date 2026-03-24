FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Python deps
RUN pip install --no-cache-dir requests

# Copy source
COPY src/ ./src/
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

# /app/data is the persistent volume mount point
# entrypoint.sh symlinks left/ right/ cortex/ from there into src/
RUN mkdir -p /app/data

ENV PYTHONUNBUFFERED=1
ENV PORT=8643

EXPOSE 8643

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s \
  CMD curl -f http://localhost:8643/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
