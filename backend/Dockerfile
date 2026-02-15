FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Support for China mirror (set USE_CN_MIRROR=true to enable)
ARG USE_CN_MIRROR=false
RUN if [ "$USE_CN_MIRROR" = "true" ]; then \
        if [ -f /etc/apt/sources.list ]; then \
            sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list; \
        fi; \
        if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
            sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources; \
        fi; \
    fi

# Install packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p uploads

# Copy and set up entrypoint script
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Environment variables for entrypoint (can be overridden)
ENV POSTGRES_HOST=medicare_postgres \
    POSTGRES_USER=medicare_user \
    POSTGRES_PASSWORD=medicare123456 \
    POSTGRES_DB=medicareai

ENTRYPOINT ["/app/entrypoint.sh"]
