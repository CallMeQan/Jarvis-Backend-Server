FROM python:3.12.10


RUN apt-get update && \
    apt-get install -y cmake build-essential


RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY . .


# TODO: Add environment variables for production
# Check docker-compose.yaml


ENV PYTHONUNBUFFERED=1
CMD ["python", "-u", "run.py"]