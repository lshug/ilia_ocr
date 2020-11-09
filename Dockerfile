FROM lshug/uvicorn-gunicorn-fastapi-tesserocr-tensorflow:python3.8

COPY ./server /app/app
