FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
WORKDIR /app

CMD ["python", "usage.py"]

# docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t rnagabhyrava/plexplaylistsync:<tag> --push .