# Stage 1: Build stage
FROM python:3.12.5-alpine3.19 AS builder

# Set environment variables to avoid Python cache and ensure reliable builds
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apk add --no-cache build-base libffi-dev

# Install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

# Stage 2: Runtime stage (minimal final image)
FROM python:3.12.5-alpine3.19

# Set working directory
WORKDIR /app

# Copy only installed dependencies from builder stage
COPY --from=builder /install /usr/local

RUN mkdir app

# Copy application code
ADD . ./app
ADD application.py .

RUN python -m pip uninstall -y pip && \
    apk --purge del apk-tools

RUN addgroup -S python && adduser -S python -G python
USER python:python

EXPOSE 8080
CMD ["uvicorn", "application:APP", "--host", "0.0.0.0", "--port", "8080", "--reload"]
