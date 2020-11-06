FROM lshug/uvicorn-gunicorn-fastapi-tesserocr-tensorflow:python3.8

ENV MAX_WORKERS 1
s
COPY ./server /app/app
