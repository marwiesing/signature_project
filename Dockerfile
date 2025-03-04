FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"]

