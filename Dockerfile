FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app


WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy everything
COPY src/ ./src
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Expose Gunicorn port
EXPOSE 5000

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]
