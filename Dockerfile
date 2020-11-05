FROM lshug/uvicorn-gunicorn-fastapi-tesserocr-tensorflow:python3.8

#Copy server files
COPY ./server /app/app
COPY ./model_training/model.h5 /app/app/model.h5
