FROM lshug/uvicorn-gunicorn-fastapi-tesserocr-tensorflow:python3.8

#Copy server files
COPY ./server /app/app
