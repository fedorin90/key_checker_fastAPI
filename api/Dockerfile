FROM python:3.12-slim

# -----------------------------
# ENV
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

WORKDIR /app

# -----------------------------
# System deps for Chromium
# -----------------------------
RUN apt-get update && apt-get install -y \
    ca-certificates \
    wget \
    fonts-liberation \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    libxshmfence1 \
    libxrender1 \
    libxext6 \
    libegl1 \
    libgl1 \
    libxkbcommon0 \
    --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Pipenv
# -----------------------------
RUN pip install --no-cache-dir pipenv

# -----------------------------
# Python deps
# -----------------------------
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

# -----------------------------
# Install Playwright browsers
# ❗ SAME PYTHON ❗
# -----------------------------
RUN python -m playwright install chromium


# -----------------------------
# App code
# -----------------------------
COPY . .

# -----------------------------
# Run
# -----------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
